# Cairn:Perception Object Detection Example

This example shows the Cairn Open Perception Stack in action, running inference models on a camera.

Start by cloning the project, and providing a compatible model.
`topo clone https://github.com/Arm-Examples/cairn-perception-object-detection.git`

## Pre-release
The following steps only apply pre-release: 

Provide your Artifactory username and access token. The token is used for both
private service images and the SDK wheel; the model token is only needed if
the Hugging Face model requires authentication. The default model is
`Arm/yolo26n-640-int8-onnx-raspberrypi5`.

Copy `.env.example` to `.env` and fill in `ARTIFACTORY_USERNAME` and
`ARTIFACTORY_TOKEN` (and `HF_TOKEN` if needed). `.env` is ignored by Git and
Topo reads it during deployment. If credentials are already exported in your
shell, do not overwrite them by sourcing an empty template.

```sh
cp .env.example .env
# Edit .env with your credentials.
```

Authenticate the host Docker daemon to pull the service images. In bash,
sh, or zsh:

```sh
set -a; . ./.env; set +a
printf '%s' "$ARTIFACTORY_TOKEN" | docker login edge-ai-tooling--sdk-docker-registry.artifactory.eu02.arm.com --username "$ARTIFACTORY_USERNAME" --password-stdin
```

For fish, export the values from `.env` before running `docker login`:

```fish
for line in (string match -rv '^\s*(#|$)' < .env)
    set -l entry (string split -m1 = -- $line)
    set -gx $entry[1] $entry[2]
end
printf '%s' "$ARTIFACTORY_TOKEN" | docker login edge-ai-tooling--sdk-docker-registry.artifactory.eu02.arm.com --username "$ARTIFACTORY_USERNAME" --password-stdin
```

## Deploy

Deploy to a remote or local target using [Topo](https://developer.arm.com/dev-docs/topo/introduction/install/).
Your target will need a USB web camera, or a Pi Camera plugged in.

```sh
topo deploy --target pi5-rod
```
On success, a command will be printed to ssh and print out the inferences run on the container.

Stop the stack when finished:
```sh
topo stop --target pi5-rod
```
