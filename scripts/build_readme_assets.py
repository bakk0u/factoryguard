"""Regenerate the README's self-contained SVG graphics. Standard-library only."""
from pathlib import Path
from html import escape
import math
OUT=Path(__file__).resolve().parents[1]/'docs/images/readme'
BG='#070b18';LINE='#273650';WHITE='#eef5ff';MUTED='#aabbd5';BLUE='#438cff';PINK='#ff69c8';YELLOW='#ffe46b'
def text(x,y,s,size=18,c=WHITE,w=400):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{c}" font-weight="{w}">{escape(s)}</text>'
def rect(x,y,w,h,c=BG,r=12,stroke=LINE):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c}" stroke="{stroke}"/>'
def circle(x,y,r,c='none',stroke=BLUE):
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="{stroke}"/>'
def shell(w,h,title,b):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><defs><linearGradient id="spectrum"><stop stop-color="{BLUE}"/><stop offset=".6" stop-color="{PINK}"/><stop offset="1" stop-color="{YELLOW}"/></linearGradient><radialGradient id="glow"><stop stop-color="#163778" stop-opacity=".65"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient></defs><style>text{{font-family:Arial,Helvetica,sans-serif}}.spin{{animation:spin 16s linear infinite}}.pulse{{animation:pulse 4s ease-in-out infinite}}.trace{{stroke-dasharray:350;animation:draw 8s ease-in-out infinite}}@keyframes spin{{to{{transform:rotate(360deg)}}}}@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}@keyframes draw{{0%{{stroke-dashoffset:350}}65%,100%{{stroke-dashoffset:0}}}}@media(prefers-reduced-motion:reduce){{.spin,.pulse,.trace{{animation:none;opacity:1;stroke-dashoffset:0}}}}</style>{rect(1,1,w-2,h-2,r=22)}{b}</svg>'''
def bearing(x,y,scale=1):
 b=circle(0,0,145,'url(#glow)','none')
 for r in [89,64,31]:b+=circle(0,0,r,stroke=BLUE)
 balls=''
 for angle in range(0,360,45):
  a=math.radians(angle);balls+=circle(round(76*math.cos(a),2),round(76*math.sin(a),2),10,BG,PINK if angle==0 else BLUE)
 b+='<g class="spin">'+balls+'</g>'
 b+='<path d="M-115 0h28l9 -10 10 17 9 -46 13 74 14 -86 14 77 12 -42 11 24 13 -10 14 2h66" fill="none" stroke="'+YELLOW+'" stroke-width="2" class="trace"/>'
 return f'<g transform="translate({x} {y}) scale({scale})">{b}</g>'
def hero(mobile):
 w,h=(440,540) if mobile else (1000,355)
 b=text(30,42,'APPLIED ML / BEARING INVESTIGATION',12,BLUE,700)
 b+=text(30,106,'FactoryGuard',47 if mobile else 66,WHITE,700)
 b+=text(30,151 if mobile else 158,'Signals into context.',26 if mobile else 32,BLUE)
 if mobile:
  b+=text(30,187,'Explore vibration, forecasts and temperature.',16,MUTED)
  b+=bearing(220,337,1.1)
  b+=text(30,488,'REAL LAB RESULTS · BROWSER DASHBOARD',12,MUTED,700)
 else:
  b+=text(30,207,'Investigate vibration and temperature',21,MUTED)
  b+=text(30,237,'alongside forecasts and operating conditions.',21,MUTED)
  b+=text(30,303,'REAL LAB RESULTS · BROWSER DASHBOARD',12,MUTED,700)
  b+=bearing(804,171,1.15)
 b+=rect(30,h-17,w-60,2,'url(#spectrum)',1,'none')
 return shell(w,h,'FactoryGuard — signals into context. Bearing investigation with real laboratory results.',b)
def workflow(mobile):
 w,h=(440,580) if mobile else (1000,260)
 b=text(28,40,'THE INVESTIGATION WORKFLOW',12,BLUE,700)
 stages=[('01','Locate the change',['Choose a bearing run','and an observation or period.'],BLUE),('02','Inspect the context',['Compare forecasts, speed,','load, gaps and warnings.'],PINK),('03','Capture the evidence',['Keep investigation notes','and export a period report.'],YELLOW)]
 for i,(num,title,lines,c) in enumerate(stages):
  x,y=(28,65+i*163) if mobile else (28+i*324,66)
  ww=384 if mobile else 296
  b+=rect(x,y,ww,144,'#0d1527')+text(x+18,y+31,num,16,c,700)
  b+=text(x+18,y+65,title,21,WHITE,700)
  for j,s in enumerate(lines):b+=text(x+18,y+95+j*23,s,16,MUTED)
  b+='<g class="pulse">'+circle(x+ww-25,y+27,4,c,c)+'</g>'
 return shell(w,h,'Locate the change, inspect its operating context, capture the investigation evidence.',b)
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 for mobile in [False,True]:
  suffix='-mobile' if mobile else ''
  for name,fn in [('hero',hero),('workflow',workflow)]:
   (OUT/f'{name}{suffix}.svg').write_text(fn(mobile),encoding='utf-8')
 print('Generated four README graphics.')
