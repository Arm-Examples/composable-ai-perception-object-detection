# Cairn: Perception Object Detection Example

This example shows the [Composable AI Runtimes](https://github.com/arm/composable-ai-runtimes)
Perception Stack in action, running inference models on a camera.

Start by cloning the project:
`topo clone https://github.com/Arm-Examples/composable-ai-perception-object-detection.git`

The default model is [UltraFace RFB-320 INT8](https://huggingface.co/Arm/ultraface-rfb-320-onnx-raspberry),
which detects faces rather than general objects. To use another compatible model,
pass `OPK_HF_DETECTION_MODEL=<Hugging Face repository>` to `topo clone`.

## Deploy

Deploy to a remote or local target using [Topo](https://developer.arm.com/dev-docs/topo/introduction/install/).
Your target will need a USB web camera, or a Pi Camera plugged in.
Replace `[user@]host` below with your SSH destination or SSH config alias.

```sh
topo deploy --target [user@]host
```
On success, a command will be printed to ssh and print out the inferences run on the container.

Inference runs continuously until you stop the stack:
```sh
topo stop --target [user@]host
```
