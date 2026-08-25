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
    // Generate subtle floating items positioned safely behind content
    const generated = Array.from({ length: 18 }).map((_, idx) => {
      const IconComponent = ICON_COMPONENTS[idx % ICON_COMPONENTS.length];
      const size = Math.floor(Math.random() * 16) + 22; // 22px to 38px
      
      // Random starting positions
      const startX = Math.random() * 92;
      const startY = Math.random() * 92;
      
      // Gentle movement offsets
      const driftX = (Math.random() - 0.5) * 20;
      const driftY = (Math.random() - 0.5) * 20;
      
      // Smooth duration
      const duration = Math.random() * 25 + 25;
      const delay = Math.random() * -50;

      // Soft, balanced opacities (18%-25%) that don't obscure text
      const colors = [
        'text-teal-800/20',
        'text-indigo-800/20',
        'text-purple-800/20',
        'text-rose-700/20',
        'text-emerald-800/20',
        'text-amber-700/20',
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
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      {/* Background Mesh Gradient */}
      <div className="live-aurora absolute inset-0" />
      <div className="absolute inset-0 opacity-[0.06] bg-[linear-gradient(rgba(15,118,110,0.18)_1px,transparent_1px),linear-gradient(90deg,rgba(15,118,110,0.18)_1px,transparent_1px)] bg-[size:56px_56px]" />

      {/* Floating Animated Icons behind content */}
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
              scale: [1, 1.1, 0.95, 1],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: item.duration,
              delay: item.delay,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <IconComponent size={item.size} strokeWidth={1.75} />
          </motion.div>
        );
      })}
    </div>
  );
}
