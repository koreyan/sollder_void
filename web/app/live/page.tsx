'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ScanSearch, CheckCircle2, AlertCircle, RefreshCw, ArrowRight } from 'lucide-react';

export default function LiveDemoPage() {
  const [image, setImage] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000");
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      setBackendUrl(`http://${hostname}:8000`);
    }
  }, []);

  // Step 1: Generate Fake Image
  const generateImage = async () => {
    setIsGenerating(true);
    setImage(null);
    setResult(null);
    
    try {
      const res = await fetch(`${backendUrl}/api/generate`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        setImage(data.image_base64);
      }
    } catch (err) {
      console.error("Generation failed", err);
      alert("백엔드 서버가 구동 중인지 확인해주세요 (Port 8000)");
    } finally {
      setIsGenerating(false);
    }
  };

  // Step 2: Analyze Image
  const analyzeImage = async () => {
    if (!image) return;
    setIsAnalyzing(true);
    
    try {
      // Base64 to Blob
      const base64Data = image.split(',')[1];
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/jpeg' });
      
      const formData = new FormData();
      formData.append('file', blob, 'generate.jpg');
      
      const res = await fetch(`${backendUrl}/api/predict`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.status === 'success') {
        setResult(data);
      }
    } catch (err) {
      console.error("Analysis failed", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Draw BBoxes when result changes
  useEffect(() => {
    if (result && canvasRef.current && image) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const img = new Image();
      img.onload = () => {
        // Match canvas size to container width while maintaining aspect ratio
        const containerWidth = containerRef.current?.offsetWidth || 640;
        const scale = containerWidth / img.width;
        
        canvas.width = containerWidth;
        canvas.height = img.height * scale;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        // Draw boxes
        result.boxes.forEach((box: any) => {
          const x = box.x * scale;
          const y = box.y * scale;
          const w = box.width * scale;
          const h = box.height * scale;
          
          ctx.strokeStyle = '#10b981'; // Green for boxes
          ctx.lineWidth = 3;
          ctx.strokeRect(x, y, w, h);
          
          // Label
          ctx.fillStyle = '#10b981';
          ctx.font = 'bold 12px Inter, sans-serif';
          const label = `Void ${Math.round(box.confidence * 100)}%`;
          const labelWidth = ctx.measureText(label).width;
          ctx.fillRect(x, y - 20, labelWidth + 10, 20);
          ctx.fillStyle = 'white';
          ctx.fillText(label, x + 5, y - 5);
        });
      };
      img.src = image;
    }
  }, [result, image]);

  return (
    <div className="container" style={{ maxWidth: '900px' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>실시간 AI 불량 판독 시연</h1>
        <p className="text-muted" style={{ fontSize: '1.125rem' }}>
          AI가 불량 데이터를 직접 생성하고, 탐지 모델이 이를 실시간으로 판독하는 과정을 체험해 보세요.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
        
        {/* Control Panel (Mobile Sticky) */}
        <div className="card mobile-sticky-bottom" style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '0.75rem', 
          padding: '1.25rem',
          flexWrap: 'wrap'
        }}>
          <button 
            className="btn btn-primary" 
            onClick={generateImage}
            disabled={isGenerating || isAnalyzing}
            style={{ flex: 1, minWidth: '140px' }}
          >
            {isGenerating ? <RefreshCw className="spin" size={18} /> : <Sparkles size={18} />}
            {isGenerating ? "생성 중..." : "데이터 생성"}
          </button>
          
          {image && !result && (
            <button 
              className="btn btn-secondary" 
              onClick={analyzeImage}
              disabled={isAnalyzing}
              style={{ flex: 1, minWidth: '140px', backgroundColor: 'var(--accent)', color: 'white' }}
            >
              {isAnalyzing ? <RefreshCw className="spin" size={18} /> : <ScanSearch size={18} />}
              {isAnalyzing ? "분석 중..." : "불량 판독"}
            </button>
          )}

          {result && (
            <button className="btn btn-secondary" onClick={generateImage} style={{ flex: 1, minWidth: '140px' }}>
              <RefreshCw size={18} /> 다시 생성
            </button>
          )}
        </div>

        {/* Display Area (Full width on mobile) */}
        <div ref={containerRef} className="card mobile-full" style={{ 
          minHeight: '350px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden',
          padding: 0,
          marginBottom: '5rem' // Spacer for sticky buttons on mobile
        }}>
          <AnimatePresence mode="wait">
            {!image && !isGenerating && (
              <motion.div 
                key="placeholder"
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                exit={{ opacity: 0 }}
                className="text-muted"
                style={{ textAlign: 'center' }}
              >
                <div style={{ marginBottom: '1rem', opacity: 0.2 }}>
                  <Sparkles size={64} />
                </div>
                <p>위의 버튼을 눌러 새로운 X-ray 영상을 생성해 주세요.</p>
              </motion.div>
            )}

            {isGenerating && (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }}
                className="text-muted"
              >
                <RefreshCw size={48} className="spin" style={{ marginBottom: '1rem' }} />
                <p>AI가 새로운 불량 패턴을 생성하고 있습니다...</p>
              </motion.div>
            )}

            {/* 이미지 표시 (항상 유지) */}
            {image && (
              <motion.div 
                key="image-container"
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }}
                style={{ position: 'relative', width: '100%' }}
              >
                {/* 결과가 없을 때는 일반 이미지, 결과가 있을 때는 캔버스 */}
                {!result ? (
                  <img 
                    src={image} 
                    style={{ width: '100%', height: 'auto', display: 'block' }} 
                    alt="Generated Solder Pad"
                  />
                ) : (
                  <canvas ref={canvasRef} style={{ width: '100%', height: 'auto', display: 'block' }} />
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Result Overlay Badge */}
          {result && (
            <motion.div
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              style={{
                position: 'absolute',
                bottom: '1rem',
                left: '1rem',
                right: '1rem',
                backgroundColor: 'rgba(15, 17, 21, 0.95)',
                backdropFilter: 'blur(10px)',
                padding: '1.25rem',
                borderRadius: '12px',
                border: '1px solid var(--card-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                zIndex: 10
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: result.verdict === "Defect" ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                  color: result.verdict === "Defect" ? '#ef4444' : '#10b981'
                }}>
                  {result.verdict === "Defect" ? <AlertCircle size={24} /> : <CheckCircle2 size={24} />}
                </div>
                <div>
                  <h2 style={{ fontSize: '1.125rem', marginBottom: '0.125rem' }}>
                    최종 판정: <span style={{ color: result.verdict === "Defect" ? '#ef4444' : '#10b981' }}>{result.verdict === "Defect" ? "불량 (Defect)" : "정상 (Normal)"}</span>
                  </h2>
                  <p className="text-muted" style={{ fontSize: '0.75rem' }}>
                    Void 면적 비율: <strong>{result.void_ratio_percent}%</strong> (판정 기준: 3.0%)
                  </p>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <p className="text-muted" style={{ fontSize: '0.75rem', marginBottom: '0.125rem' }}>검출된 Void 수</p>
                <p style={{ fontSize: '1.25rem', fontWeight: 700 }}>{result.count}개</p>
              </div>
            </motion.div>
          )}
        </div>

        {/* Technical Info (Dynamic) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div className="card" style={{ padding: '1.5rem', borderLeft: image ? '4px solid var(--primary)' : '1px solid var(--card-border)' }}>
            <h4 style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '0.875rem', textTransform: 'uppercase' }}>1단계: 불량 이미지 생성</h4>
            <p style={{ fontSize: '1.125rem', fontWeight: 600 }}>DCGAN 모델 (Track A)</p>
            <p className="text-muted" style={{ fontSize: '0.875rem' }}>
              {image ? "✅ 이미지 생성이 완료되었습니다." : "랜덤 노이즈로부터 가상 데이터를 생성합니다."}
            </p>
          </div>
          <div className="card" style={{ padding: '1.5rem', borderLeft: result ? (result.verdict === 'Defect' ? '4px solid #ef4444' : '4px solid #10b981') : '1px solid var(--card-border)' }}>
            <h4 style={{ color: 'var(--accent)', marginBottom: '0.5rem', fontSize: '0.875rem', textTransform: 'uppercase' }}>2단계: 실시간 객체 탐지</h4>
            <p style={{ fontSize: '1.125rem', fontWeight: 600 }}>YOLOv8s 모델 (Proposed)</p>
            <p className="text-muted" style={{ fontSize: '0.875rem' }}>
              {result ? `✅ ${result.count}개의 Void를 검출했습니다.` : (image ? "AI가 불량 영역을 분석하고 있습니다..." : "생성된 데이터를 바탕으로 판독을 수행합니다.")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
