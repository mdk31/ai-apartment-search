import aws_cdk as core
import aws_cdk.assertions as assertions

from ai_apartment_search.ai_apartment_search_stack import AiApartmentSearchStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ai_apartment_search/ai_apartment_search_stack.py
# def test_sqs_queue_created():
    # app = core.App()
    # stack = AiApartmentSearchStack(app, "ai-apartment-search")
    # template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
