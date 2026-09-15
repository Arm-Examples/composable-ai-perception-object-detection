# Cairn:Perception Classification Example

This example shows the Cairn Open Perception Stack in action, running inference models on a camera.

Start by cloning the project and providing a compatible example.
`topo clone <url>`

## Pre-release
The following steps only apply pre-release: 

Copy the credential template and set both values:

```sh
cp .env.example .env
set -a; . ./.env; set +a
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
topo deloy --target pi5-grimes
```
On success, a command will be printed to ssh and print out the inferences run on the container.

Stop the stack when finished:
```sh
topo stop --target user@my-linux-device
```
