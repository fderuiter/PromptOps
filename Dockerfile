# Use a slim Python 3.11 image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and package files first to leverage build cache
COPY requirements.txt pyproject.toml uv.lock ./
COPY promptops ./promptops
COPY tools ./tools
COPY studio ./studio

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set PYTHONPATH to ensure python can find everything correctly
ENV PYTHONPATH="/app"

# Run the MCP server using standard input/output (stdio) channels
ENTRYPOINT ["python", "mcp_server.py"]
