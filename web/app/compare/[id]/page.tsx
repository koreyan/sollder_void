import fs from 'fs';
import path from 'path';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import BBoxViewer from './BBoxViewer';

export default async function ComparePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const dataPath = path.join(process.cwd(), 'public', 'data', 'predictions.json');
  const fileContents = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(fileContents);
  
  const imageId = parseInt(id, 10);
  const image = data.images.find((img: any) => img.id === imageId);

  if (!image) {
    return <div className="container" style={{ padding: '4rem 2rem', textAlign: 'center' }}>Image not found.</div>;
  }

  const imageSrc = `/data/images/${image.filename}`;

  return (
    <div className="container">
      <div style={{ marginBottom: '2rem' }}>
        <Link href="/gallery" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          <ArrowLeft size={16} /> Back to Gallery
        </Link>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{image.original_name}</h1>
        <p className="text-muted">
          Compare the detection results between Baseline (Real Data) and Proposed (Real + Synthetic) models.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '2rem'
      }}>
        <BBoxViewer 
          src={imageSrc}
          boxes={image.baseline.boxes}
          color="#3b82f6" // Primary Blue
          title="Baseline Model"
          originalWidth={image.width}
          originalHeight={image.height}
        />
        
        <BBoxViewer 
          src={imageSrc}
          boxes={image.proposed.boxes}
          color="#10b981" // Accent Green
          title="Proposed Model"
          originalWidth={image.width}
          originalHeight={image.height}
        />
      </div>
    </div>
  );
}
