'use client';

import { QRCodeSVG } from 'qrcode.react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, QrCode, Scan, ShieldCheck } from 'lucide-react';

import { useState, useEffect } from 'react';

export default function Home() {
  const [demoUrl, setDemoUrl] = useState("https://sollder-void-demo.vercel.app");

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setDemoUrl(window.location.origin + "/live");
    }
  }, []);

  return (
    <div className="container">
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 200px)',
        textAlign: 'center'
      }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ maxWidth: '800px' }}
        >
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            color: 'var(--primary)',
            borderRadius: '999px',
            marginBottom: '2rem',
            fontWeight: 500,
            fontSize: '0.875rem'
          }}>
            <ShieldCheck size={16} />
            Phase 5 실시간 시연 시스템 가동 중
          </div>
          
          <h1 style={{ fontSize: '3.5rem', fontWeight: 800, marginBottom: '1.5rem', letterSpacing: '-0.03em' }}>
            AI 기반 <span style={{ color: 'var(--primary)' }}>솔더 Void</span> 불량 검출 시스템
          </h1>
          
          <p className="text-muted" style={{ fontSize: '1.25rem', maxWidth: '800px', margin: '0 auto 3rem', lineHeight: 1.6 }}>
            DCGAN 생성 데이터로 강화된 YOLOv8 모델을 통해 반도체 솔더 패드 내의 미세한 기포(Void)를 실시간으로 탐지하고 판정합니다.
          </p>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '4rem' }}>
              <Link href="/live" className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1.25rem', boxShadow: '0 0 20px rgba(59, 130, 246, 0.4)' }}>
                라이브 시연 시작하기 <ArrowRight size={24} style={{ marginLeft: '0.5rem' }} />
              </Link>
            </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="card"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '2rem',
            padding: '2rem',
            background: 'linear-gradient(145deg, var(--card-bg), rgba(15, 17, 21, 0.5))',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
            border: '1px solid rgba(255,255,255,0.05)'
          }}
        >
          <div style={{
            padding: '1rem',
            backgroundColor: 'white',
            borderRadius: '12px'
          }}>
            <QRCodeSVG value={demoUrl} size={150} level={"H"} />
          </div>
          
          <div style={{ textAlign: 'left' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Scan size={24} color="var(--primary)" />
              Live Mobile Demo
            </h3>
            <p className="text-muted" style={{ marginBottom: '1.5rem', maxWidth: '300px' }}>
              Scan the QR code to interact with the dashboard directly from your smartphone during the presentation.
            </p>
            <div style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '0.5rem',
              fontSize: '0.875rem',
              color: '#94a3b8',
              backgroundColor: 'rgba(255,255,255,0.05)',
              padding: '0.5rem 1rem',
              borderRadius: '6px'
            }}>
              <QrCode size={16} />
              {demoUrl}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
