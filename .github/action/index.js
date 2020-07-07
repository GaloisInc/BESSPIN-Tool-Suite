const child_process = require("child_process");
const process = require("process");

const toInpt = (n) => `INPUT_${n.replace(/ /g, "_").toUpperCase()}`;
const getInput = (n) => (process.env[toInpt(n)] || "").trim();
const group = (g) => console.log(`::group::${g}`);
const endGroup = () => console.log("::endgroup::");

const env = ["-e HOME=/home/besspinuser", "-e CI=true"].concat(
  [
    "JOB",
    "REF",
    "SHA",
    "REPOSITORY",
    "REPOSITORY_OWNER",
    "RUN_ID",
    "RUN_NUMBER",
    "ACTOR",
    "WORKFLOW",
    "HEAD_REF",
    "BASE_REF",
    "EVENT_NAME",
    "WORKSPACE",
    "ACTION",
    "EVENT_PATH",
    "ACTIONS=true",
  ].map((e) => `-e GITHUB_${e}`),
  ["ssh-key", "run", "image"].map((e) => `-e ${toInpt(e)}`),
  ["RUNTIME_URL", "RUNTIME_TOKEN", "CACHE_URL"].map((e) => `-e ACTIONS_${e}`),
  ["OS", "TOOL_CACHE", "TEMP", "WORKSPACE"].map((e) => `-e RUNNER_${e}`)
);

function runDocker(image) {
  const sshKey = getInput("ssh-key");
  const run = getInput("run");
  const hash = require("crypto").randomBytes(4).toString("hex");

  const work = "/root/actions-runner/_work";
  const docker = child_process.spawn(
    "docker",
    [
      "run",
      "--rm",
      `--name ${image.replace(/[^a-z0-9]+/gi, "")}-${hash}`,
      `--label=${hash}`,
      "--privileged",
      "--user=root",
      "--network=host",
      "--workdir /github/workspace",
      ...env,
      "-v /var/run/docker.sock:/var/run/docker.sock",
      `-v ${work}/_temp/_github_home:/github/home`,
      `-v ${work}/_temp/_github_workflow:/github/workflow`,
      `-v ${work}/SSITH-FETT-Target/SSITH-FETT-Target:/github/workspace`,
      image,
      "bash",
      "-c",
      `'export PATH=/opt/Xilinx/Vivado/2019.1/bin:/opt/Xilinx/Vivado_Lab/2019.1/bin:$PATH
      . /opt/Xilinx/Vivado_Lab/2019.1/settings64.sh
      eval "$(ssh-agent -s)"
      ssh-add <(echo "${sshKey}")
      . /home/besspinuser/.nix-profile/etc/profile.d/nix.sh'"
      ${run.replace(/"/g, '\\"')}"`,
    ],
    { shell: true, stdio: "inherit" }
  );
  docker.on("exit", (c) => endGroup() || process.exit(c));
}

try {
  // This works because the machines with the self hosted runner have already logged into artifactory
  const image =
    getInput("image") || "artifactory.galois.com:5008/fett-target:ci";

  console.log(`Hostname is: ${require("os").hostname()}`);
  group("Pulling docker image");
  const child = child_process.spawn(`docker pull ${image}`, {
    shell: true,
    stdio: "inherit",
  });
  child.on("exit", (c) =>
    c === 0 ? endGroup() || runDocker(image) : process.exit(c)
  );
} catch (error) {
  process.stderr.write(error.message);
  process.exitCode = 1;
}
