
#!/bin/bash

echo "🚀 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip aiofiles dnspython

LIMIT=${1:-50}
echo "🔍 Starting Fastly SNI Scanner with limit: $LIMIT"
python fastly_sni_scanner_optimized.py $LIMIT

echo "📂 Showing results:"
cat fastly_sni_working.txt
