const child_process = require("child_process");
const process = require("process");

const getInput = (name) =>
  (process.env[`INPUT_${name.replace(/ /g, "_").toUpperCase()}`] || "").trim();

const env = [
  "-e INPUT_SSH-KEY",
  "-e INPUT_RUN",
  "-e HOME",
  "-e CI=true",
  "-e GITHUB_JOB",
  "-e GITHUB_REF",
  "-e GITHUB_SHA",
  "-e GITHUB_REPOSITORY",
  "-e GITHUB_REPOSITORY_OWNER",
  "-e GITHUB_RUN_ID",
  "-e GITHUB_RUN_NUMBER",
  "-e GITHUB_ACTOR",
  "-e GITHUB_WORKFLOW",
  "-e GITHUB_HEAD_REF",
  "-e GITHUB_BASE_REF",
  "-e GITHUB_EVENT_NAME",
  "-e GITHUB_WORKSPACE",
  "-e GITHUB_ACTION",
  "-e GITHUB_EVENT_PATH",
  "-e GITHUB_ACTIONS=true",
  "-e ACTIONS_RUNTIME_URL",
  "-e ACTIONS_RUNTIME_TOKEN",
  "-e ACTIONS_CACHE_URL",
  "-e RUNNER_OS",
  "-e RUNNER_TOOL_CACHE",
  "-e RUNNER_TEMP",
  "-e RUNNER_WORKSPACE",
];

try {
  const sshKey = getInput("ssh-key");
  const run = getInput("run");
  // This works because the VM with the self hosted runner has already pulled the image.
  const image = "artifactory.galois.com:5008/fett-target:ci";

  const work = "/home/gitlab-runner/actions-runner/_work";
  const docker = child_process.spawn(
    "docker",
    [
      "run",
      "--rm",
      `--name ${image.replace(/[^a-z0-9]+/gi, "")}`,
      "--privileged",
      "--network=host",
      "--workdir /github/workspace",
      ...env,
      '-v "/var/run/docker.sock":"/var/run/docker.sock" ',
      `-v "${work}/_temp/_github_home":"/github/home"        `,
      `-v "${work}/_temp/_github_workflow":"/github/workflow" `,
      `-v "${work}/SSITH-FETT-Target/SSITH-FETT-Target":"/github/workspace"`,
      image,
      "bash",
      "-c",
      `"export HOME=/home/besspinuser
      export PATH=/opt/Xilinx/Vivado/2019.1/bin:/opt/Xilinx/Vivado_Lab/2019.1/bin:$PATH
      . /opt/Xilinx/Vivado_Lab/2019.1/settings64.sh
      eval $(ssh-agent -s)
      ssh-add <(echo \\"${sshKey}\\")
      . /home/besspinuser/.nix-profile/etc/profile.d/nix.sh
      ${run.replace(/"/g, '\\"')}"`,
    ],
    { shell: true, stdio: "inherit" }
  );
  process.exitCode = docker.exitCode;
} catch (error) {
  process.stderr.write(error.message);
  process.exitCode = 1;
}
