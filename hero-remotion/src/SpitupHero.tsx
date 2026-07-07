import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  staticFile,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";

/**
 * Each shot is a close-up crop of client / stock footage.
 * scale + tx/ty push the frame past the burned-in SPITUP logo (top-right)
 * and subtitles (bottom) on the client clips. A slow zoom adds cinematic life.
 */
export type Shot = {
  id: string;
  src: string;
  scale: number; // base crop zoom
  tx: number; // horizontal push in % (positive = hide right edge / logo)
  ty: number; // vertical push in % (positive = hide bottom edge / subtitle)
  zoom: number; // extra scale added across the shot (Ken Burns)
  drift?: number; // subtle horizontal drift in % across the shot
};

export const SHOT_FRAMES = 108; // 3.6s per shot
export const REPRISE_FRAMES = 44; // short loop-back tail
export const XFADE = 24; // crossfade length

// Order chosen for tonal continuity so the hard loop seam (office → office) is soft.
export const SHOTS: Shot[] = [
  // All shots pulled wider so more of each scene reads. Client clips have a floor of
  // ~1.24 — below that the burned-in subtitle creeps back at the bottom. The ty push
  // keeps the caption cropped; the stock phone clip has no caption so it goes widest.
  { id: "office", src: "clips/spitup_office.mp4", scale: 1.24, tx: 0, ty: 9.5, zoom: 0.03, drift: 1 },
  { id: "glasses", src: "clips/spitup_glasses.mp4", scale: 1.30, tx: 4, ty: 8.5, zoom: 0.05, drift: -2 },
  // (removed the dark "woman on mobile" stock shot — montage is now all client footage)
  { id: "hands", src: "clips/docteur_hands.mp4", scale: 1.36, tx: 3, ty: 9.5, zoom: 0.05, drift: -3 },
  { id: "headset", src: "clips/docteur_headset.mp4", scale: 1.32, tx: 4, ty: 8.5, zoom: 0.05, drift: 2 },
];

// Total frames of the whole TransitionSeries (kept in sync with Root's composition).
export const TOTAL_FRAMES =
  SHOTS.length * SHOT_FRAMES + REPRISE_FRAMES - SHOTS.length * XFADE;

const ShotView: React.FC<{ shot: Shot; frames: number }> = ({ shot, frames }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, frames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = shot.scale + shot.zoom * p;
  const driftX = (shot.drift ?? 0) * p;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0B0B", overflow: "hidden" }}>
      <OffthreadVideo
        src={staticFile(shot.src)}
        muted
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translate(${shot.tx + driftX}%, ${shot.ty}%)`,
          // Light, neutral grade — the page adds its own darkening overlay on top.
          filter: "contrast(1.05) saturate(1.04) brightness(1.02)",
        }}
      />
      {/* subtle warm gold wash + vignette to unify the mixed footage */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(120% 120% at 50% 40%, rgba(201,168,118,0.10), rgba(11,11,11,0) 55%)",
          mixBlendMode: "soft-light",
        }}
      />
      <AbsoluteFill
        style={{
          boxShadow: "inset 0 0 240px 60px rgba(0,0,0,0.45)",
        }}
      />
    </AbsoluteFill>
  );
};

export const SpitupHero: React.FC = () => {
  const t = () => fade();
  const timing = linearTiming({ durationInFrames: XFADE });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0B0B0B" }}>
      <TransitionSeries>
        {SHOTS.map((shot, i) => (
          <React.Fragment key={shot.id}>
            <TransitionSeries.Sequence durationInFrames={SHOT_FRAMES}>
              <ShotView shot={shot} frames={SHOT_FRAMES} />
            </TransitionSeries.Sequence>
            {/* transition after every shot (the last one bridges into the reprise) */}
            <TransitionSeries.Transition presentation={t()} timing={timing} />
            {i === SHOTS.length - 1 ? (
              <TransitionSeries.Sequence durationInFrames={REPRISE_FRAMES}>
                <ShotView shot={SHOTS[0]} frames={SHOT_FRAMES} />
              </TransitionSeries.Sequence>
            ) : null}
          </React.Fragment>
        ))}
      </TransitionSeries>
    </AbsoluteFill>
  );
};
