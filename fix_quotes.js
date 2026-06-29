const fs = require('fs');

// Fix search/page.tsx
let path = 'd:/Research Mind/frontend/app/(dashboard)/dashboard/search/page.tsx';
let content = fs.readFileSync(path, 'utf8');
content = content.replace('results for "<span', 'results for {"\\""}<span');
content = content.replace('</span>"', '</span>{"\\""}');
fs.writeFileSync(path, content, 'utf8');
console.log('Fixed search/page.tsx');

// Fix layout.tsx
path = 'd:/Research Mind/frontend/app/(dashboard)/layout.tsx';
content = fs.readFileSync(path, 'utf8');
content = content.replace('No results for "', 'No results for {"\\""}');
content = content.replace('"</p>', '{"\\""}</p>');
fs.writeFileSync(path, content, 'utf8');
console.log('Fixed layout.tsx');