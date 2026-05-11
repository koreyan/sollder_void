import fs from 'fs';
import path from 'path';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight, ImageIcon } from 'lucide-react';

interface Prediction {
  id: number;
  filename: string;
  original_name: string;
  width: number;
  height: number;
  baseline: { total_detections: number };
  proposed: { total_detections: number };
}

export default function GalleryPage() {
  const dataPath = path.join(process.cwd(), 'public', 'data', 'predictions.json');
  const fileContents = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(fileContents);
  const images: Prediction[] = data.images;

  return (
    <div className="container">
      <div style={{ marginBottom: '3rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ImageIcon color="var(--primary)" />
          Test Set Gallery
        </h1>
        <p className="text-muted" style={{ fontSize: '1.125rem' }}>
          Select an image to compare the detection performance between the Baseline and Proposed models.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '2rem'
      }}>
        {images.map((img) => (
          <Link href={`/compare/${img.id}`} key={img.id}>
            <div className="card gallery-card">
              <div style={{ 
                position: 'relative', 
                width: '100%', 
                aspectRatio: '1', 
                backgroundColor: '#000',
                borderRadius: '8px',
                overflow: 'hidden',
                marginBottom: '1rem'
              }}>
                <Image 
                  src={`/data/images/${img.filename}`} 
                  alt={img.original_name}
                  fill
                  style={{ objectFit: 'contain' }}
                />
              </div>
              
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem', wordBreak: 'break-all' }}>
                  {img.filename}
                </h3>
                
                <div style={{ 
                  display: 'flex', 
                  gap: '1rem', 
                  marginTop: 'auto',
                  paddingTop: '1rem',
                  borderTop: '1px solid var(--card-border)',
                  fontSize: '0.875rem'
                }}>
                  <div style={{ color: '#94a3b8' }}>
                    <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{img.baseline.total_detections}</span> Base
                  </div>
                  <div style={{ color: '#94a3b8' }}>
                    <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{img.proposed.total_detections}</span> Prop
                  </div>
                  <div style={{ marginLeft: 'auto', color: 'var(--primary)', display: 'flex', alignItems: 'center' }}>
                    Compare <ArrowRight size={16} style={{ marginLeft: '0.25rem' }} />
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
