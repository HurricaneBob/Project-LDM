// Halftone dot pattern over a soft violet glow — shown behind the
// conversation while the model is responding. Pure CSS (see `.halftone-bg`
// in src/index.css). Place inside a parent with `position: relative` and
// `overflow-hidden`.
//
// Props:
//   visible — when true, fades in and breathes; when false, fades out (350ms).

export default function AiResponseBackground({ visible = false }) {
  return (
    <div
      aria-hidden
      className={`halftone-bg${visible ? ' is-visible' : ''}`}
    />
  );
}
