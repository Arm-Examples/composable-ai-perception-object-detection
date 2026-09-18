# Cairn:Perception Object Detection Example

This example shows the Cairn Open Perception Stack in action, running inference models on a camera.

Start by cloning the project, and providing a compatible model.
`topo clone https://github.com/Arm-Examples/cairn-perception-object-detection.git`

## Pre-release
The following steps only apply pre-release: 

Copy the credential template and set both values. Set
`OPK_HF_DETECTION_MODEL` to either `Arm/Yolo-v11` or its full Hugging Face URL
to select the object-detection model.

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

Authenticate Docker to the private service-image registry. `gh auth token`
uses the active GitHub CLI account; its token needs `read:packages`.

```sh
gh auth token | docker login ghcr.io --username "$(gh api user --jq .login)" --password-stdin
```

## Deploy

Deploy to a remote or local target using [Topo](https://developer.arm.com/dev-docs/topo/introduction/install/).
Your target will need a USB web camera, or a Pi Camera plugged in.

```sh
topo deloy --target user@my-linux-device
```
On success, a command will be printed to ssh and print out the inferences run on the container.

Stop the stack when finished:
```sh
topo stop --target user@my-linux-device
```
