"use client";

import { motion, useReducedMotion } from "@/components/motion/fade-in";

/** Full-bleed Nordic desk scene — papers, desk edge, teal ink. Not a card. */
export function DeskScene({ className }: { className?: string }) {
  const reduce = useReducedMotion();

  return (
    <div className={className} aria-hidden>
      <svg
        viewBox="0 0 960 720"
        className="h-full w-full object-cover"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="deskWash" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="oklch(0.94 0.02 210)" />
            <stop offset="55%" stopColor="oklch(0.96 0.015 185)" />
            <stop offset="100%" stopColor="oklch(0.92 0.025 230)" />
          </linearGradient>
          <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="oklch(0.995 0.004 230)" />
            <stop offset="100%" stopColor="oklch(0.97 0.01 230)" />
          </linearGradient>
          <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="8" />
          </filter>
        </defs>

        <rect width="960" height="720" fill="url(#deskWash)" />

        {/* Desk surface */}
        <path
          d="M0 520 H960 V720 H0 Z"
          fill="oklch(0.88 0.02 70 / 0.35)"
        />
        <path
          d="M0 518 H960"
          stroke="oklch(0.55 0.04 70 / 0.25)"
          strokeWidth="2"
        />

        {/* Soft teal bloom */}
        <motion.ellipse
          cx="720"
          cy="280"
          rx="220"
          ry="160"
          fill="oklch(0.55 0.09 185 / 0.14)"
          filter="url(#soft)"
          animate={reduce ? undefined : { opacity: [0.55, 0.85, 0.55], y: [0, -8, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Back paper */}
        <motion.g
          initial={reduce ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15 }}
        >
          <rect
            x="380"
            y="120"
            width="360"
            height="420"
            rx="4"
            fill="url(#paper)"
            stroke="oklch(0.82 0.02 230)"
            strokeWidth="1.5"
            transform="rotate(4 560 330)"
          />
          {[0, 1, 2, 3, 4, 5, 6].map((i) => (
            <line
              key={`b-${i}`}
              x1="420"
              y1={180 + i * 42}
              x2="700"
              y2={184 + i * 42}
              stroke="oklch(0.78 0.02 230)"
              strokeWidth="2"
              transform="rotate(4 560 330)"
              opacity={0.7}
            />
          ))}
        </motion.g>

        {/* Front notebook */}
        <motion.g
          initial={reduce ? false : { opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.28 }}
        >
          <rect
            x="220"
            y="160"
            width="400"
            height="460"
            rx="3"
            fill="url(#paper)"
            stroke="oklch(0.8 0.02 230)"
            strokeWidth="1.5"
            transform="rotate(-3 420 390)"
          />
          {/* Binding */}
          <rect
            x="236"
            y="168"
            width="18"
            height="444"
            fill="oklch(0.48 0.09 185 / 0.85)"
            transform="rotate(-3 420 390)"
          />
          {/* Title line */}
          <rect
            x="290"
            y="210"
            width="240"
            height="10"
            rx="2"
            fill="oklch(0.35 0.03 250 / 0.55)"
            transform="rotate(-3 420 390)"
          />
          {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
            <line
              key={`f-${i}`}
              x1="290"
              y1={250 + i * 36}
              x2={i % 3 === 2 ? 480 : 560}
              y2={248 + i * 36}
              stroke="oklch(0.72 0.02 230)"
              strokeWidth="2.5"
              transform="rotate(-3 420 390)"
            />
          ))}
          {/* Teal highlight mark */}
          <rect
            x="290"
            y="358"
            width="180"
            height="14"
            rx="2"
            fill="oklch(0.55 0.09 185 / 0.22)"
            transform="rotate(-3 420 390)"
          />
        </motion.g>

        {/* Small index card */}
        <motion.g
          initial={reduce ? false : { opacity: 0, y: 22, rotate: -8 }}
          animate={{ opacity: 1, y: 0, rotate: -6 }}
          transition={{ duration: 0.65, delay: 0.4 }}
        >
          <rect
            x="620"
            y="420"
            width="220"
            height="140"
            rx="4"
            fill="oklch(0.99 0.005 230)"
            stroke="oklch(0.8 0.02 230)"
            strokeWidth="1.5"
          />
          <rect x="648" y="452" width="120" height="8" rx="2" fill="oklch(0.48 0.09 185)" />
          <line x1="648" y1="482" x2="800" y2="482" stroke="oklch(0.78 0.02 230)" strokeWidth="2" />
          <line x1="648" y1="508" x2="770" y2="508" stroke="oklch(0.78 0.02 230)" strokeWidth="2" />
        </motion.g>

        {/* Pencil */}
        <motion.g
          initial={reduce ? false : { opacity: 0, x: 20 }}
          animate={
            reduce
              ? { opacity: 1 }
              : { opacity: 1, x: 0, rotate: [12, 14, 12] }
          }
          transition={
            reduce
              ? { duration: 0.5, delay: 0.5 }
              : { duration: 6, delay: 0.5, rotate: { repeat: Infinity, duration: 5, ease: "easeInOut" } }
          }
          style={{ transformOrigin: "780px 340px" }}
        >
          <path
            d="M720 300 L860 360 L852 376 L712 316 Z"
            fill="oklch(0.82 0.08 85)"
          />
          <path d="M860 360 L878 368 L870 384 L852 376 Z" fill="oklch(0.35 0.03 250)" />
          <path d="M720 300 L712 316 L728 308 Z" fill="oklch(0.7 0.05 70)" />
        </motion.g>
      </svg>
    </div>
  );
}
