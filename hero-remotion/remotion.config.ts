import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// The source clips are muted already; the hero background plays without sound.
Config.setChromiumOpenGlRenderer("angle");
