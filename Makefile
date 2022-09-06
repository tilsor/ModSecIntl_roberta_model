PB=pb/roberta.pb.go pb/roberta_grpc.pb.go

all: roberta.so

roberta.so: $(PB) roberta.go go.mod
	go build -buildmode=plugin roberta.go

# Generate both pb.go files from proto file:
$(PB): roberta.proto.intermediate
.INTERMEDIATE: roberta.proto.intermediate
roberta.proto.intermediate: roberta.proto
	protoc --go_out=. --go-grpc_out=. $<

clean:
	rm -f $(PB) roberta.so
