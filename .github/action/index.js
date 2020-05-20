const child_process = require("child_process");
const process = require("process");

const getInput = (name) =>
  (process.env[`INPUT_${name.replace(/ /g, "_").toUpperCase()}`] || "").trim();

const env = [
  ["INPUT_SSH-KEY", "INPUT_RUN", "HOME", "CI = true"],
  [
    ["JOB", "REF", "SHA", "REPOSITORY", "REPOSITORY_OWNER"],
    ["RUN_ID", "RUN_NUMBER", "ACTOR", "WORKFLOW", "HEAD_REF", "BASE_REF"],
    ["EVENT_NAME", "WORKSPACE", "ACTION", "EVENT_PATH", "ACTIONS=true"],
  ].flatMap((e) => `GITHUB_${e}`),
  ["RUNTIME_URL", "RUNTIME_TOKEN", "CACHE_URL"].map((e) => `ACTIONS_${e}`),
  ["OS", "TOOL_CACHE", "TEMP", "WORKSPACE"].map((e) => `RUNNER_${e}`),
].flatMap((e) => ` -e ${e}`);

try {
  const sshKey = getInput("ssh-key");
  const run = getInput("run");
  // This works because the VM with the self hosted runner has already pulled the image.
  const image = "artifactory.galois.com:5008/fett-target:ci";

  const work = "/home/gitlab-runner/actions-runner/_work";
  const docker = child_process.spawn(
    "docker",
    [
      `run --rm --name ${image.replace(/[^a-z0-9]+/gi, " ")}`,
      `--privileged=true --network=host`,
      `--workdir /github/workspace`,
      `${env} --entrypoint ".github/docker/entrypoint.sh"`,
      '-v "/var/run/docker.sock":"/var/run/docker.sock" ',
      `-v "${work}/_temp/_github_home":"/github/home"        `,
      `-v "${work}/_temp/_github_workflow":"/github/workflow" `,
      `-v "${work}/SSITH-FETT-Target/SSITH-FETT-Target": "/github/workspace"`,
      image,
      "bash",
      "-c",
      `export HOME=/home/besspinuser
       export PATH=/opt/Xilinx/Vivado/2019.1/bin:/opt/Xilinx/Vivado_Lab/2019.1/bin:$PATH
       . /opt/Xilinx/Vivado_Lab/2019.1/settings64.sh
       eval $(ssh-agent -s)
       ssh-add <(echo "${sshKey}")
       . /home/besspinuser/.nix-profile/etc/profile.d/nix.sh
       ${run}`,
    ],
    { shell: "/bin/bash" }
  );
  docker.stdout.on("data", (data) => process.stdout.write(`stdout: ${data}`));
  docker.stderr.on("data", (data) => process.stderr.write(`${data}`));
  process.exitCode = docker.exitCode;
} catch (error) {
  process.stderr.write(error.message);
  process.exitCode = 1;
}
