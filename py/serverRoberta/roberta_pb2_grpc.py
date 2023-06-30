# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import serverRoberta.roberta_pb2 as roberta__pb2


class modSecIntlStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Detect = channel.unary_unary(
                '/pb.modSecIntl/Detect',
                request_serializer=roberta__pb2.modSecIntlRequest.SerializeToString,
                response_deserializer=roberta__pb2.modSecIntlResponse.FromString,
                )


class modSecIntlServicer(object):
    """Missing associated documentation comment in .proto file"""

    def Detect(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_modSecIntlServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Detect': grpc.unary_unary_rpc_method_handler(
                    servicer.Detect,
                    request_deserializer=roberta__pb2.modSecIntlRequest.FromString,
                    response_serializer=roberta__pb2.modSecIntlResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.modSecIntl', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class modSecIntl(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def Detect(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/pb.modSecIntl/Detect',
            roberta__pb2.modSecIntlRequest.SerializeToString,
            roberta__pb2.modSecIntlResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
