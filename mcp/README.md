# MCP Tools for Fortune Teller

This directory contains Model Context Protocol (MCP) tools that provide specialized functionality for the Fortune Teller system.

## Directory Structure

```
mcp/
├── README.md              # This file
├── mcp_config.yaml        # MCP tools configuration
├── mcp_manager.py         # Centralized MCP manager
├── tools/                 # MCP tool implementations
│   ├── tarot_picker.py    # Tarot card random picker
│   └── bazi_converter.py  # BaZi Four Pillars converter
└── servers/               # Future MCP servers
```

## Available MCP Tools

### 1. Tarot Card Picker (`tarot_picker.py`)

**Purpose**: Provides high-quality randomness for authentic tarot card readings.

**Features**:
- Complete 78-card tarot deck (Major + Minor Arcana)
- Fisher-Yates shuffle algorithm for true randomness
- Cryptographic randomness using Python's `secrets` module
- Support for reversed cards
- Bilingual card names (Chinese + English)

**Commands**:
- `draw <count> <allow_reversed>` - Draw random cards
- `info` - Get deck information

**Example**:
```bash
python mcp/tools/tarot_picker.py draw 3 true
```

### 2. BaZi Converter (`bazi_converter.py`)

**Purpose**: Converts birth date/time to Chinese Four Pillars (八字) with accurate calculations.

**Features**:
- Accurate Four Pillars calculation (年月日时柱)
- Complete Heavenly Stems and Earthly Branches (天干地支)
- Five Elements analysis (五行分布)
- Yin-Yang balance calculation (阴阳平衡)
- Day Master identification (日主)

**Commands**:
- `convert <year> <month> <day> [hour]` - Convert to BaZi
- `info` - Get system information

**Example**:
```bash
python mcp/tools/bazi_converter.py convert 1990 7 25 14
```

## MCP Manager

The `MCPManager` class provides centralized management of all MCP tools:

**Features**:
- Tool registry and discovery
- Standardized invocation interface
- Error handling and timeout management
- Detailed logging and result formatting
- Health checking capabilities

**Usage**:
```python
from mcp.mcp_manager import mcp_manager, draw_tarot_cards, convert_to_bazi

# Draw 3 tarot cards
result = await draw_tarot_cards(3, allow_reversed=True)

# Convert birth date to BaZi
result = await convert_to_bazi(1990, 7, 25, 14)

# Health check all tools
health = await mcp_manager.health_check()
```

## Configuration

MCP tools are configured via `mcp_config.yaml`:

- Tool definitions and parameters
- Timeout settings
- Logging preferences
- Future server configurations

## Adding New MCP Tools

1. Create the tool script in `mcp/tools/`
2. Implement the standard MCP interface:
   - Accept command as first argument
   - Return JSON responses with `success` field
   - Support `info` command for metadata
3. Register the tool in `mcp_manager.py`
4. Update `mcp_config.yaml` with tool configuration
5. Add documentation to this README

## Error Handling

All MCP tools follow consistent error handling:

- **Success**: `{"success": true, "data": {...}}`
- **Failure**: `{"success": false, "error": "description"}`
- **Timeout**: Automatic timeout after configured seconds
- **Logging**: All invocations and results are logged

## Security Considerations

- Tools run in isolated subprocess environments
- Timeout protection prevents hanging processes
- Input validation in tool implementations
- No network access required (all tools are local)

## Performance

- Tools are lightweight Python scripts
- Fast startup and execution (< 1 second typical)
- Minimal memory footprint
- Concurrent execution support

## Future Enhancements

Planned MCP additions:
- **I Ching Divination Tool**: Hexagram generation and interpretation
- **Chinese Calendar Converter**: Solar/Lunar calendar conversions
- **Feng Shui Calculator**: Direction and element analysis
- **Numerology Tool**: Name and number analysis
