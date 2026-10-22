import asyncio
import os

from cairn import CameraService, Notification, NotificationService
from cairn.perception import (
    BoxDetections,
    PerceptionResult,
    PerceptionService,
    PerceptionWorkflow,
)

WORKFLOW_DURATION_SECONDS = float(os.environ.get("WORKFLOW_DURATION_SECONDS", "60"))


async def main() -> None:
    camera_configuration = None
    cameras = CameraService().list_cameras()
    for pixel_format in ("RGB", "YUY2"):
        for camera in cameras:
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

    service = await PerceptionService.connect()
    session = await service.deploy(workflow)
    if session.topics.results is None:
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

    async with NotificationService() as notifications:
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
