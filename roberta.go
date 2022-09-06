package main

import (
	"context"
	"net/url"
	"regexp"
	re "regexp"
	"strconv"
	"strings"
	"time"

	"google.golang.org/grpc"

	pb "roberta/pb"

	lg "github.com/tilsor/ModSecIntl_logging/logging"
)

var urlParam string
var thresholdParam float64

func InitPlugin(params map[string]string) error {
	logger := lg.Get()

	urlParam = params["url"]
	var err error
	thresholdParam, err = strconv.ParseFloat(params["distance_threshold"], 64)

	if err == nil {
		logger.Println(lg.DEBUG, "[roberta plugin] initialization complete")
	}

	return err
}

func ProcessRequest(transactionID, req string) (float64, error) {
	return analyze(transactionID, urlParam, req)
}

func analyze(transactionID, addr, logs string) (float64, error) {
	ctxt, _ := context.WithTimeout(context.Background(), 5*time.Second)
	conn, err := grpc.DialContext(ctxt, addr, grpc.WithInsecure())
	if err != nil {
		return 0.0, err
	}
	defer conn.Close()

	client := pb.NewModSecIntlClient(conn)
	req := &pb.ModSecIntlRequest{
		Metrics: createData(transactionID, logs),
	}

	resp, err := client.Detect(context.Background(), req)

	if err != nil {
		return 0.0, err
	}
	data := resp.Response[0]
	return getClass(transactionID, float64(data.Decision)), err
}

func createData(transactionID, log string) []*pb.ModSecLog {
	out := make([]*pb.ModSecLog, 1)
	log = parser(transactionID, log)
	m := pb.ModSecLog{
		Name: "request",
	}
	out[0] = &m
	out[0].Value = log
	return out
}

func parser(transactionID, log string) string {
	logger := lg.Get()

	request := getRequest(log)
	result := setAttr(request["method"][0])
	result += setAttr(request["protocol"][0])
	result += setHeaderAttr(request["headers"])
	result += setQueryAttr(request["body"][0])

	logger.TPrintf(lg.DEBUG, transactionID, "[roberta plugin] log analyzing: %s", result)

	return result
}

func getRequest(log string) map[string][]string {
	geek := re.MustCompile("\n")
	geek2 := re.MustCompile(" ")

	split := geek.Split(log, -1)
	line1 := geek2.Split(split[0], -1)
	request := make(map[string][]string)

	request["method"] = []string{line1[0]}
	request["url"] = []string{line1[1]}
	request["protocol"] = []string{line1[2]}

	headersIndex := 0
	headers := make([]string, len(split))
	body := ""
	for i := 1; i < len(split); i++ {
		if strings.Index(split[i], ":") != -1 {
			headers[headersIndex] = split[i]
			headersIndex++
		} else {
			body += split[i]
		}
	}
	request["headers"] = headers
	request["body"] = []string{body}

	return request
}

func setQueryAttr(query string) string {
	result := ""
	if query == "" {
		return result
	}
	geek := re.MustCompile("&")
	params := geek.Split(query, -1)

	for i := 0; i < len(params); i++ {
		pos := strings.Index(params[i], "=")
		if pos == -1 {
			decodedStr, err := url.QueryUnescape(params[i])
			result += decodedStr
			if err != nil {
				result += params[i]
			}
		} else {
			name := params[i][0:pos]
			value := params[i][pos+1 : len(params[i])]
			decodedStr, err := url.QueryUnescape(name)
			result += decodedStr
			if err != nil {
				result += name
			}
			result += " "
			decodedStr, err = url.QueryUnescape(value)
			result += decodedStr
			if err != nil {
				result += value
			}
		}
		result += " "
	}

	return result
}

func setHeaderAttr(headers []string) string {
	if len(headers) == 0 {
		return ""
	}
	res := ""
	for i := 0; i < len(headers); i++ {
		header := strings.ToLower(headers[i])
		if header != "" {
			if !match("^host", header) && !match("^x-forwarded-for:", header) && !match("^via:", header) && !match("^client-ip:", header) && !match("^referer:", header) && !match("^cookie:", header) && !match("^etag:", header) && !match("^if-none-match:", header) && !match("^set-cookie", header) && !match("^last-modified:", header) && !match("^if-modified-since:", header) && !match("^----:", header) && !match("^----:", header) && !match("^accept-charset:", header) && !match("^accept-encoding:", header) && !match("^proxy-authorization:", header) && !match("^if-range:", header) && !match("^if-match:", header) && !match("^from:", header) && !match("^upgrade:", header) && !match("^if-unmodified-since:", header) && !match("^ua-color:", header) && !match("^authorization:", header) && !match("^max-forwards:", header) && !match("^ua-cpu:", header) && !match("^ua-disp:", header) && !match("^ua-os:", header) && !match("^ua-pixels:", header) && !match("^x-serial-number:", header) && !match("^cache-control:", header) && !match("^accept-language:", header) && !match("^trailer:", header) && !match("^expect:", header) && !match("^pragma:", header) && !match("^range:", header) {
				if match("^cookie", header) {
					header = strings.ReplaceAll(header, ";", " ")
					geek := re.MustCompile(" ")
					cookies := geek.Split(header, -1)
					for y := 0; y < len(cookies); y++ {
						eqPos := strings.Index(cookies[y], "=")
						if eqPos == -1 {
							res += cookies[y] + " "
						} else {
							res += cookies[y][0:eqPos] + " " + cookies[y][eqPos+1:len(cookies[y])] + " "
						}
					}
				} else {
					res += header + " "
				}
			}
		}
	}
	return res
}

func setAttr(str string) string {
	if str != "" && "UNKNOWN" != str {
		return str + " "
	} else {
		return ""
	}

}

func getClass(transactionID string, dist float64) float64 {
	logger := lg.Get()

	var attackProbability float64
	if dist >= thresholdParam {
		attackProbability = 0.0
		logger.TPrintf(lg.DEBUG, transactionID, "[roberta plugin] distance %.3f >= %.3f, returning %.3f probability", dist, thresholdParam, attackProbability)
	} else {
		attackProbability = 1.0
		logger.TPrintf(lg.DEBUG, transactionID, "[roberta plugin] distance %.3f < %.3f, returning %.3f probability", dist, thresholdParam, attackProbability)
	}

	return attackProbability
}

func match(pattern string, text string) bool {
	matched, _ := regexp.Match(pattern, []byte(text))
	return matched
}

func main() {}
