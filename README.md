# Cairn:Perception Object Detection Example

This example shows the Cairn Open Perception Stack in action, running inference models on a camera.

Start by cloning the project, and providing a compatible model.
`topo clone https://github.com/Arm-Examples/cairn-perception-object-detection.git`

## Pre-release
The following steps only apply pre-release: 

Copy the credential template and fill in the credentials. Set
`OPK_HF_DETECTION_MODEL` to a compatible Hugging Face repository ID or its full URL
to select the object-detection model. It defaults to
[`Arm/yolo26n-640-int8-onnx-raspberrypi5`](https://huggingface.co/Arm/yolo26n-640-int8-onnx-raspberrypi5).
The existing `OPK_HF_*` input and `x-topo` hints are retained for Topo/AI Portal;
the repository must provide `arm/opk/opchain.json`, `arm/opk/model.json` and the
referenced model file.

bash, sh, zsh, etc.
```sh
cp .env.example .env
set -a; . ./.env; set +a
```

or for fish:
```fish
for line in (string match -rv '^\s*(#|$)' < .env)
    set -l entry (string split -m1 = -- $line)
    set -gx $entry[1] $entry[2]
end
```

Authenticate Docker to the private service-image registry using your Artifactory
username and token (`ARTIFACTORY_USERNAME` and `ARTIFACTORY_TOKEN`):

```sh
printf '%s' "$ARTIFACTORY_TOKEN" | docker login edge-ai-tooling--sdk-docker-registry.artifactory.eu02.arm.com --username "$ARTIFACTORY_USERNAME" --password-stdin
```

The service images and Python SDK are pinned to the `20260930144748` development
build (service revision `f805dd1a`).

## Networking

Camera uses host networking for device uevents. Messaging and perception use the
Compose network; Redis (6379) and perception gRPC (50053) are published only on
host loopback. Perception uses its image's default command, `/models` directory
and `messaging-service` Redis endpoint; camera frames use the shared PipeWire
socket rather than host networking.

The example application retains host networking so `CameraService()`,
`PerceptionService.connect()` and `NotificationService()` can use the SDK's
loopback defaults without endpoint environment variables. Bridging the application
would require explicit endpoints, including a route to the host camera service.

## Deploy

Deploy to a remote or local target using [Topo](https://developer.arm.com/dev-docs/topo/introduction/install/).
Your target will need a USB web camera, or a Pi Camera plugged in.

```sh
topo deploy --target user@my-linux-device
```
On success, a command will be printed to ssh and print out the inferences run on the container.

Stop the stack when finished:
```sh
topo stop --target user@my-linux-device
```
