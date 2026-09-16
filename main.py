import asyncio
import os

from cairn_sdk import CameraService, Notification, NotificationService
from cairn_sdk.perception import PerceptionResult, PerceptionService, PerceptionWorkflow
from cairn_sdk.perception.types import BoxDetectionsT

CAMERA_ENDPOINT = os.environ.get("CAMERA_ENDPOINT", "http://127.0.0.1:50051")
PERCEPTION_ENDPOINT = os.environ.get("PERCEPTION_ENDPOINT", "http://127.0.0.1:50053")
REDIS_ENDPOINT = os.environ.get("REDIS_ENDPOINT", "redis://127.0.0.1:6379/0")
WORKFLOW_DURATION_SECONDS = float(os.environ.get("WORKFLOW_DURATION_SECONDS", "60"))


async def main() -> None:
    camera = CameraService(CAMERA_ENDPOINT).list_cameras()[0]
    stream_configurations = await camera.get_stream_configurations(
        resolution=(640, 480),
        pixel_format="YUY2",
    )
    if not stream_configurations:
        raise RuntimeError("camera has no 640x480 YUY2 stream at 30 fps")

    workflow = PerceptionWorkflow(
        "detection-workflow",
        stream_configurations[0],
    )
    workflow.infer("objects", "detection-model")

    service = await PerceptionService.connect(PERCEPTION_ENDPOINT)
    session = await service.deploy(workflow)
    if session.topics is None:
        raise RuntimeError("deployment returned no results topic")

    async def print_result(notification: Notification) -> None:
        result = PerceptionResult.decode(notification.payload)
        detections: list[str] = [
            f"{detection.text.decode() if isinstance(detection.text, bytes) else detection.text} "
            f"{detection.confidence:.0%}"
            for payload in result.payloads(BoxDetectionsT)
            for detection in payload.detections or []
        ]
        print(
            f"result topic={notification.channel} "
            f"detections={', '.join(detections) or 'none'}"
        )

    async with NotificationService(REDIS_ENDPOINT) as notifications:
        subscription = await notifications.subscribe(
            session.topics.results, print_result
        )
        try:
            await asyncio.sleep(WORKFLOW_DURATION_SECONDS)
        finally:
            await notifications.unsubscribe(subscription)
            await session.stop()


if __name__ == "__main__":
    asyncio.run(main())
