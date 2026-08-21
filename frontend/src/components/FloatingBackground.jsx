// src/components/FloatingBackground.jsx
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpen, 
  GraduationCap, 
  Pencil, 
  Calculator, 
  FileText, 
  Compass, 
  Award,
  Sparkles
} from 'lucide-react';

const ICON_COMPONENTS = [
  BookOpen,
  GraduationCap,
  Pencil,
  Calculator,
  FileText,
  Compass,
  Award,
  Sparkles
];

export default function FloatingBackground() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    // Generate floating items with random positions, paths, and durations
    const generated = Array.from({ length: 18 }).map((_, idx) => {
      const IconComponent = ICON_COMPONENTS[idx % ICON_COMPONENTS.length];
      const size = Math.floor(Math.random() * 24) + 20; // 20px to 44px
      
      // Random starting positions (viewport relative)
      const startX = Math.random() * 100; // 0% to 100%
      const startY = Math.random() * 100; // 0% to 100%
      
      // Random movement offsets
      const driftX = (Math.random() - 0.5) * 40; // -20% to +20%
      const driftY = (Math.random() - 0.5) * 40; // -20% to +20%
      
      // Duration & delays for natural offsets
      const duration = Math.random() * 30 + 30; // 30s to 60s
      const delay = Math.random() * -60; // Start at pre-drifting phase (negative delay)

      // Random custom colors for study materials floating
      const colors = [
        'text-indigo-500/10',
        'text-purple-500/10',
        'text-pink-500/10',
        'text-blue-500/10',
        'text-teal-500/10',
      ];
      const color = colors[idx % colors.length];

      return {
        id: idx,
        IconComponent,
        size,
        startX,
        startY,
        driftX,
        driftY,
        duration,
        delay,
        color
      };
    });

    setItems(generated);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div className="live-aurora absolute inset-0" />
      <div className="absolute inset-0 opacity-[0.08] bg-[linear-gradient(rgba(255,255,255,0.16)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.16)_1px,transparent_1px)] bg-[size:56px_56px]" />

      {items.map(item => {
        const { IconComponent } = item;
        return (
          <motion.div
            key={item.id}
            className={`absolute ${item.color}`}
            style={{
              left: `${item.startX}%`,
              top: `${item.startY}%`,
            }}
            animate={{
              x: [`0vw`, `${item.driftX}vw`, `0vw`],
              y: [`0vh`, `${item.driftY}vh`, `0vh`],
              rotate: [0, 360],
            }}
            transition={{
              duration: item.duration,
              delay: item.delay,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <IconComponent size={item.size} strokeWidth={1.5} />
          </motion.div>
        );
      })}
    </div>
  );
}
