// src/components/Footer.jsx
import { motion } from 'framer-motion';
import { Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="relative z-10 mt-16 py-8 border-t border-stone-300/60 text-center text-xs text-stone-600 font-semibold tracking-wide">
      <p className="inline-flex items-center justify-center gap-1.5 select-none">
        <span>Made with</span>
        <motion.span
          animate={{
            scale: [1, 1.25, 1, 1.25, 1],
            filter: [
              'drop-shadow(0 0 2px rgba(244, 63, 94, 0.4))',
              'drop-shadow(0 0 8px rgba(244, 63, 94, 0.8))',
              'drop-shadow(0 0 2px rgba(244, 63, 94, 0.4))',
              'drop-shadow(0 0 8px rgba(244, 63, 94, 0.8))',
              'drop-shadow(0 0 2px rgba(244, 63, 94, 0.4))'
            ]
          }}
          transition={{
            duration: 1.6,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
          className="inline-flex items-center justify-center text-rose-500 cursor-pointer"
          title="Made with love for all MHT-CET students"
        >
          <Heart size={15} className="fill-rose-500 text-rose-500" />
        </motion.span>
        <span>for MHT-CET Aspirants</span>
      </p>
    </footer>
  );
}
