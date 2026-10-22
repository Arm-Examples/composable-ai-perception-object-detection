# Cairn:Perception Object Detection Example

This example shows the Cairn Open Perception Stack in action, running inference models on a camera.

Start by cloning the project, and providing a compatible model.
`topo clone https://github.com/Arm-Examples/composable-ai-perception-object-detection.git`

## Deploy

Deploy to a remote or local target using [Topo](https://developer.arm.com/dev-docs/topo/introduction/install/).
Your target will need a USB web camera, or a Pi Camera plugged in.

```sh
topo deploy --target pi5-rod
```
On success, a command will be printed to ssh and print out the inferences run on the container.

Inference runs continuously until you stop the stack:
```sh
topo stop --target pi5-rod
```
