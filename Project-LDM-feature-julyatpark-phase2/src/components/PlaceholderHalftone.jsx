/**
 * Procedural halftone placeholder. Renders a dot-pattern shape sized to a 1:1 box.
 * Replace by setting `image` on the persona data + dropping the file in /public/personas/.
 *
 * Each `shape` produces a distinct silhouette using radial-gradient dots
 * masked to a recognizable form.
 */

function generateDots(shape, color) {
  // Returns an array of circle elements positioned within a 200x200 viewBox.
  // Density and clustering differ per shape to give each persona an identity.
  const dots = [];
  const gridSize = 16; // 16x16 grid of potential dot positions
  const cellSize = 200 / gridSize;

  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      const cx = col * cellSize + cellSize / 2;
      const cy = row * cellSize + cellSize / 2;
      const nx = (cx - 100) / 100; // normalized -1..1
      const ny = (cy - 100) / 100;

      let intensity = 0;

      switch (shape) {
        case 'lightning': {
          // Diagonal jagged arrow
          const onPath =
            Math.abs(nx - ny * 0.6) < 0.25 && Math.abs(ny) < 0.85;
          intensity = onPath ? 1 - Math.abs(nx - ny * 0.6) / 0.25 : 0;
          break;
        }
        case 'target': {
          // Concentric rings
          const r = Math.sqrt(nx * nx + ny * ny);
          const ringDist = Math.abs((r % 0.28) - 0.14);
          intensity = r < 0.9 ? 1 - ringDist / 0.14 : 0;
          break;
        }
        case 'network': {
          // Grid/lattice pattern
          const gridX = Math.abs(nx) < 0.85 && col % 3 === 0;
          const gridY = Math.abs(ny) < 0.85 && row % 3 === 0;
          intensity = gridX || gridY ? 1 : 0;
          break;
        }
        case 'heart': {
          // Organic blob (heart-ish)
          const r = Math.sqrt(nx * nx + (ny + 0.1) * (ny + 0.1));
          const angle = Math.atan2(ny + 0.1, nx);
          const heartR = 0.7 * (1 - Math.sin(angle) * 0.4);
          intensity = r < heartR ? 1 - r / heartR : 0;
          break;
        }
        case 'bridge': {
          // Two overlapping circles
          const leftR = Math.sqrt(
            (nx + 0.32) * (nx + 0.32) + ny * ny
          );
          const rightR = Math.sqrt(
            (nx - 0.32) * (nx - 0.32) + ny * ny
          );
          const inLeft = leftR < 0.55;
          const inRight = rightR < 0.55;
          intensity = inLeft && inRight ? 1 : inLeft || inRight ? 0.45 : 0;
          break;
        }
        default: {
          const r = Math.sqrt(nx * nx + ny * ny);
          intensity = r < 0.8 ? 1 - r / 0.8 : 0;
        }
      }

      if (intensity > 0.15) {
        const radius = Math.max(0.8, intensity * 3.2);
        dots.push(
          <circle
            key={`${row}-${col}`}
            cx={cx}
            cy={cy}
            r={radius}
            fill={color}
            opacity={Math.min(1, intensity * 1.2)}
          />
        );
      }
    }
  }
  return dots;
}

export default function PlaceholderHalftone({ shape, color }) {
  return (
    <div className="relative w-full aspect-square bg-black overflow-hidden">
      <svg
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Subtle radial backdrop for depth */}
        <defs>
          <radialGradient id={`grad-${shape}`} cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor={color} stopOpacity="0.12" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </radialGradient>
        </defs>
        <rect width="200" height="200" fill={`url(#grad-${shape})`} />
        {generateDots(shape, color)}
      </svg>
    </div>
  );
}
