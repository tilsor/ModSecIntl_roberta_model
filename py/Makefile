PB=roberta_pb2.py roberta_pb2_grpc.py

all: $(PB)

$(PB): roberta.proto.intermediate
.INTERMEDIATE: roberta.proto.intermediate
roberta.proto.intermediate: ../roberta.proto
	python -m grpc_tools.protoc \
	-I.. --python_out=serverRoberta --grpc_python_out=serverRoberta \
	../roberta.proto

clean:
	rm -f $(PB)
