'use client';

import { useEffect, useRef, useState } from 'react';

interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
  confidence: number;
}

interface BBoxViewerProps {
  src: string;
  boxes: Box[];
  color: string;
  title: string;
  originalWidth: number;
  originalHeight: number;
}

export default function BBoxViewer({ src, boxes, color, title, originalWidth, originalHeight }: BBoxViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const { clientWidth } = containerRef.current;
        // Calculate proportional height based on original image dimensions
        const clientHeight = (originalHeight / originalWidth) * clientWidth;
        setDimensions({ width: clientWidth, height: clientHeight });
      }
    };

    window.addEventListener('resize', updateSize);
    updateSize();

    return () => window.removeEventListener('resize', updateSize);
  }, [originalWidth, originalHeight]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || dimensions.width === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // High DPI scaling
    const dpr = window.devicePixelRatio || 1;
    canvas.width = dimensions.width * dpr;
    canvas.height = dimensions.height * dpr;
    
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, dimensions.width, dimensions.height);

    // Calculate scale factors from original image to current canvas size
    const scaleX = dimensions.width / originalWidth;
    const scaleY = dimensions.height / originalHeight;

    boxes.forEach((box) => {
      const x = box.x * scaleX;
      const y = box.y * scaleY;
      const w = box.w * scaleX;
      const h = box.h * scaleY;

      // Draw bounding box
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);

      // Draw confidence label background
      ctx.fillStyle = color;
      const label = `${(box.confidence * 100).toFixed(0)}%`;
      ctx.font = '12px Inter, sans-serif';
      const textWidth = ctx.measureText(label).width;
      
      ctx.fillRect(x, y - 20, textWidth + 8, 20);
      
      // Draw text
      ctx.fillStyle = '#ffffff';
      ctx.fillText(label, x + 4, y - 6);
    });

  }, [boxes, dimensions, originalWidth, originalHeight, color]);

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0, color: color }}>{title}</h3>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          {boxes.length} Voids Detected
        </div>
      </div>
      
      <div 
        ref={containerRef} 
        style={{ 
          position: 'relative', 
          width: '100%', 
          backgroundColor: '#000',
          borderRadius: '8px',
          overflow: 'hidden'
        }}
      >
        <img 
          src={src} 
          alt={title} 
          style={{ 
            width: '100%', 
            height: 'auto', 
            display: 'block' 
          }} 
        />
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }}
        />
      </div>
    </div>
  );
}
