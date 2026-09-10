const { useComposition, CompositionStage, animate, Easing } = window;

const MOTION = {
  enter: (from, to, start, end) => animate({ from, to, start, end, ease: Easing.easeOutCubic }),
  draw: (from, to, start, end) => animate({ from, to, start, end, ease: Easing.easeInOutQuad }),
  pop: (from, to, start, end) => animate({ from, to, start, end, ease: Easing.easeOutBack }),
};

const BUBBLE = "M118 75H316C377 75 421 119 421 177c0 57-44 101-105 101H171l-91 67 11-98c-32-19-51-54-51-94C40 109 73 75 118 75Z";
const WEDGE = "M300 278h121v-64Z";

const BARS = [
  { x: 118, y: 302, w: 304, h: 46 },
  { x: 118, y: 370, w: 304, h: 46 },
  { x: 118, y: 438, w: 236, h: 35 },
];

const WITH_GLYPHS = [
  "m 624.992,238 31.08,-122.472 H 638.6 L 616.088,214.984 588.2,115.528 h -16.8 l -27.216,99.456 -23.016,-99.456 H 503.696 L 535.112,238 h 17.136 L 579.632,137.368 607.856,238 Z",
  "m 676.45591,149.968 h -13.944 V 238 h 13.944 z m 0,-34.44 h -14.112 v 17.64 h 14.112 z",
  "m 724.22393,149.968 h -14.448 v -24.192 h -13.944 v 24.192 h -11.928 v 11.424 h 11.928 v 66.528 c 0,9.072 6.048,13.944 16.968,13.944 3.696,0 6.72,-0.336 11.424,-1.176 v -11.76 c -2.016,0.504 -3.864,0.672 -6.72,0.672 -6.048,0 -7.728,-1.68 -7.728,-7.896 v -60.312 h 14.448 z",
  "M 732.00782,115.528 V 238 h 13.944 v -48.552 c 0,-17.976 9.408,-29.736 23.856,-29.736 4.704,0 9.072,1.344 12.432,3.864 4.032,3.024 5.712,7.224 5.712,13.44 V 238 h 13.944 v -66.528 c 0,-14.784 -10.584,-24.024 -27.72,-24.024 -12.432,0 -19.992,3.864 -28.224,14.616 v -46.536 z",
];

const BADER_GLYPHS = [
  "m 514.268,418 h 57.072 c 14.616,0 24.36,-2.784 32.016,-9.222 7.656,-6.438 12.528,-17.052 12.528,-27.318 0,-12.528 -6.612,-22.446 -21.054,-30.798 12.528,-8.004 17.4,-15.312 17.4,-26.1 0,-8.874 -4.35,-17.922 -11.484,-24.186 -7.482,-6.438 -16.356,-9.222 -29.928,-9.222 h -56.55 z m 26.1,-105.096 h 28.362 c 12.18,0 18.444,4.872 18.444,14.268 0,9.57 -6.264,14.442 -18.444,14.442 h -28.362 z m 0,50.46 h 31.146 c 12.702,0 19.314,5.568 19.314,16.53 0,10.788 -6.612,16.356 -19.314,16.356 h -31.146 z",
  "m 709.80402,415.042 c -4.176,-4.002 -5.568,-6.786 -5.568,-11.484 v -52.2 c 0,-19.14 -13.05,-28.884 -38.454,-28.884 -25.404,0 -38.628,10.788 -40.194,32.538 h 23.49 c 1.218,-9.744 5.22,-12.876 17.226,-12.876 9.396,0 14.094,3.132 14.094,9.396 0,3.132 -1.566,5.742 -4.176,7.308 -3.306,1.74 -3.306,1.74 -15.312,3.654 l -9.744,1.74 c -18.618,3.132 -27.666,12.702 -27.666,29.58 0,16.878 11.31,28.188 28.536,28.188 10.44,0 19.836,-4.35 28.536,-13.398 0,4.872 0.522,6.612 2.784,9.396 h 26.448 z m -29.406,-34.8 c 0,14.094 -6.96,22.098 -19.314,22.098 -8.178,0 -13.224,-4.35 -13.224,-11.31 0,-7.308 3.828,-10.788 13.92,-12.876 l 8.352,-1.566 c 6.438,-1.218 7.482,-1.566 10.266,-2.958 z",
  "m 778.84198,418 h 24.36 V 291.154 h -24.36 v 45.066 c -6.09,-9.396 -14.094,-13.746 -25.926,-13.746 -22.446,0 -39.498,21.576 -39.498,49.938 0,12.702 3.828,25.578 10.092,34.626 6.438,9.222 17.922,14.964 29.406,14.964 11.832,0 19.836,-4.176 25.926,-13.572 z m -20.532,-75.168 c 12.354,0 20.532,11.832 20.532,29.928 0,17.052 -8.352,28.884 -20.532,28.884 -12.18,0 -20.532,-12.006 -20.532,-29.232 0,-17.574 8.352,-29.58 20.532,-29.58 z",
  "m 898.86197,378.676 c 0.174,-2.088 0.174,-2.958 0.174,-4.176 0,-9.396 -1.392,-18.096 -3.654,-24.708 -6.264,-17.052 -21.402,-27.318 -40.368,-27.318 -26.97,0 -43.5,19.488 -43.5,50.982 0,30.102 16.356,48.546 42.978,48.546 21.054,0 38.106,-11.832 43.5,-30.45 h -24.012 c -2.958,7.482 -9.744,11.832 -18.618,11.832 -6.96,0 -12.528,-2.958 -16.008,-8.178 -2.262,-3.48 -3.132,-7.656 -3.48,-16.53 z m -62.64,-16.182 c 1.566,-14.442 7.656,-21.402 18.444,-21.402 11.136,0 17.748,7.482 18.966,21.402 z",
  "M 908.39193,324.04 V 418 h 24.36 v -49.938 c 0,-14.268 7.134,-21.402 21.402,-21.402 2.61,0 4.35,0.174 7.656,0.696 v -24.708 c -1.392,-0.174 -1.914,-0.174 -2.958,-0.174 -11.136,0 -20.706,7.308 -26.1,20.01 V 324.04 Z",
];

function Mark({ T, C }) {
  const dash = MOTION.draw(1, 0, C.Draw + 0.15, C.Draw + 1.6)(T);
  const wedge = MOTION.pop(0, 1, C.Lines - 0.2, C.Lines + 0.45)(T);
  return (
    <g>
      <path
        d={BUBBLE}
        pathLength="1"
        fill="none"
        stroke="url(#brandGradient)"
        strokeWidth="39"
        strokeLinejoin="round"
        strokeLinecap="round"
        strokeDasharray="1 1"
        strokeDashoffset={dash}
      />
      <path
        d={WEDGE}
        fill="url(#brandGradient)"
        opacity={wedge > 0.02 ? 1 : 0}
        transform={`translate(421,278) scale(${Math.max(wedge, 0.001)}) translate(-421,-278)`}
      />
      {BARS.map((b, i) => {
        const s = C.Lines + 0.1 + i * 0.2;
        const w = MOTION.enter(0, b.w, s, s + 0.55)(T);
        const o = MOTION.enter(0, 1, s, s + 0.2)(T);
        return (
          <rect key={i} x={b.x} y={b.y} width={Math.max(w, 0.01)} height={b.h} rx="2" fill="url(#brandGradient)" opacity={o} />
        );
      })}
    </g>
  );
}

function Wordmark({ T, C }) {
  const glyph = (d, i, total, weight, start) => {
    const s = start + i * 0.075;
    const y = MOTION.enter(34, 0, s, s + 0.7)(T);
    const o = MOTION.enter(0, 1, s, s + 0.45)(T);
    return <path key={weight + i} d={d} opacity={o} transform={`translate(0,${y})`} />;
  };
  return (
    <g fill="#113b69">
      {WITH_GLYPHS.map((d, i) => glyph(d, i, WITH_GLYPHS.length, "w", C.Wordmark))}
      {BADER_GLYPHS.map((d, i) => glyph(d, i, BADER_GLYPHS.length, "b", C.Wordmark + 0.28))}
    </g>
  );
}

function LogoReveal(props) {
  const { T, CUES: C, authoredTotal } = useComposition();
  const bg = props.bg || "#f5f8fb";

  // camera: settle in, then a slow continuous drift so the frame is never static
  const settle = MOTION.enter(1.07, 1, C.Draw, C.Wordmark + 0.8)(T);
  const drift = 1 + 0.012 * Math.sin(((T - C.Hold) / 3.4) * Math.PI * 2) * (T > C.Hold ? 1 : 0);
  const out = MOTION.draw(1, 1.035, C.Reset + 0.15, authoredTotal)(T);
  const scale = settle * drift * out * (props.logoScale || 1);
  const fade = MOTION.draw(1, 0, C.Reset + 0.3, authoredTotal - 0.05)(T);

  // gradient slides slowly through the mark for a live sheen
  const sheen = 70 * Math.sin((T / 4.6) * Math.PI * 2);

  return (
    <div style={{ position: "absolute", inset: 0, background: bg, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
      <svg width="1420" height="675" viewBox="20 45 970 460" style={{ transform: `scale(${scale})`, opacity: fade }}>
        <defs>
          <linearGradient id="brandGradient" x1={60 + sheen} y1="70" x2={430 + sheen} y2="420" gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor="#25D7B9" />
            <stop offset="0.52" stopColor="#20BCCE" />
            <stop offset="1" stopColor="#2585F2" />
          </linearGradient>
        </defs>
        <Mark T={T} C={C} />
        <Wordmark T={T} C={C} />
      </svg>
    </div>
  );
}

function LogoRevealStage(props) {
  return (
    <CompositionStage
      width={1920}
      height={1080}
      scenes={window.OM_SCENES}
      playback={window.OM_PLAYBACK}
      bg={props.bg || "#f5f8fb"}
    >
      <LogoReveal bg={props.bg} logoScale={props.logoScale} />
    </CompositionStage>
  );
}

window.LogoRevealStage = LogoRevealStage;
