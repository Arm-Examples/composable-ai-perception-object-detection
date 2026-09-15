import asyncio
import os

from cairn_sdk import CameraService, Notification, NotificationService
from cairn_sdk.perception import (
    BoxDetections,
    PerceptionResult,
    PerceptionService,
    PerceptionWorkflow,
)

CAMERA_ENDPOINT = os.environ.get("CAMERA_ENDPOINT", "http://127.0.0.1:50051")
PERCEPTION_ENDPOINT = os.environ.get("PERCEPTION_ENDPOINT", "http://127.0.0.1:50053")
REDIS_ENDPOINT = os.environ.get("REDIS_ENDPOINT", "redis://127.0.0.1:6379/0")
WORKFLOW_DURATION_SECONDS = float(os.environ.get("WORKFLOW_DURATION_SECONDS", "60"))


async def main() -> None:
    camera_configuration = None
    cameras = CameraService(CAMERA_ENDPOINT).list_cameras()
    for camera in cameras:
        for pixel_format in ("RGB", "YUY2"):
            stream_configurations = await camera.get_stream_configurations(
                resolution=(640, 480),
                pixel_format=pixel_format,
                frame_rate=(30, 1),
            )
            if stream_configurations:
                camera_configuration = stream_configurations[0]
                break
        if camera_configuration is not None:
            break

    if camera_configuration is None:
        raise RuntimeError(
            "camera has no 640x480 RGB or YUY2 stream at 30 fps"
        )

    workflow = PerceptionWorkflow(
        "detection-workflow",
        camera_configuration,
    )
    workflow.infer("objects", "detection_model")

    service = await PerceptionService.connect(PERCEPTION_ENDPOINT)
    session = await service.deploy(workflow)
    if session.topics is None:
        raise RuntimeError("deployment returned no results topic")

    async def print_result(notification: Notification) -> None:
        result = PerceptionResult.decode(notification.payload)
        detections: list[str] = [
            f"{detection.text or detection.class_id} {detection.confidence:.0%}"
            for payload in result.entries
            if isinstance(payload, BoxDetections)
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
