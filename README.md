# Cairn: Perception Object Detection Example

This example shows the [Cairn](https://github.com/arm/composable-ai-runtimes) Open Perception Stack in action, running inference models on a camera.

Start by cloning the project, and providing a compatible model.
`topo clone https://github.com/Arm-Examples/composable-ai-perception-object-detection.git`

## Deploy

Deploy to a remote or local target using [Topo](https://developer.arm.com/dev-docs/topo/introduction/install/).
Your target will need a USB web camera, or a Pi Camera plugged in.
Replace `[user@]host` below with your SSH destination or SSH config alias.

```sh
topo deploy --target [user@]host
```
On success, a command will be printed to ssh and print out the inferences run on the container.

## Debug viewer

Open `http://<target-ip>:9999` in a browser on the same network to see the
camera stream with detection overlays. Use the target's IP address rather than
its SSH alias unless that alias also resolves in DNS.

The workflow enables Cairn's `DebugOutput` (the OPK debug viewer) on TCP ports
`9999` (HTTP), `8000` (WebRTC signalling), and `8001` (control). Cairn's results
WebSocket starts at `8002`, matching the viewer's inference and performance panels.
This example runs one workflow; additional sessions would use subsequent ports.
The perception service uses host networking so WebRTC's dynamically allocated
UDP media ports are reachable too; forwarding only the TCP ports over SSH is
not enough for video. The gRPC API and Redis remain bound to loopback.

The debug viewer exposes camera video and controls without authentication.
Use it only on a trusted network; do not forward these ports to the internet.

Inference runs continuously until you stop the stack:
```sh
topo stop --target [user@]host
```
