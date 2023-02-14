

# Send to single device.
from pyfcm import FCMNotification

push_service = FCMNotification(api_key="AAAAfq2WvOs:APA91bE2viBlyAy5eFQcAvT23YRkPFNLMByVp8txIzAWaR39KJCF0v2Dv0VEa9V_stGAs50Y7b-rIz-Cv_Jk1LIeY5cGscl3Axlpi9cBAiJfOkMcT2T8evRO9qcb13pXEdpZBDHpovYu")


#Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

registration_id = "cLx8jCMxVJA:APA91bHvrD_HnTNV2ImW43IWrjU6pEI4e1LMtUUExvhKhbmu4TuLZ6Bav779PT9sZncc01fMBTBoO0hBpneLEQ8akdudoc3T_jPv61Oa1WabPHO8zOgZ4HyvzNvSm7iCzol95tqAggNJ"
message_title = "Prabhakar"
message_body = "Hello New Message"
result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

print(result)

