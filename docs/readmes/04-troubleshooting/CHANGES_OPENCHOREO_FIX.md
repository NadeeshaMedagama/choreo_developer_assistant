# OpenChoreo Prevention Changes

## Summary
This document describes the changes made to ensure DevChoreo AI Assistant only provides information about WSO2's Choreo platform and explicitly rejects questions about OpenChoreo.

## Changes Made

### 1. Backend - System Prompt Updates (`backend/services/llm_service.py`)

Updated both `get_response()` and `get_response_stream()` methods to include a comprehensive system prompt that:

- Identifies the assistant as "DevChoreo" for WSO2's Choreo platform
- Explicitly instructs to ONLY provide information about WSO2's Choreo platform
- Explicitly instructs NOT to provide information about OpenChoreo
- Provides a template response for when users ask about OpenChoreo
- Ensures all responses are specific to WSO2's Choreo platform

**Example System Prompt:**
```
You are DevChoreo, an AI assistant specifically for the Choreo platform by WSO2.

IMPORTANT INSTRUCTIONS:
- You must ONLY provide information about the Choreo platform (https://wso2.com/choreo/)
- Do NOT provide information about OpenChoreo or any other platforms
- If a user asks about OpenChoreo, politely clarify that you are designed to help with the Choreo platform by WSO2, not OpenChoreo

Example response for OpenChoreo questions:
"I'm DevChoreo, an AI assistant for the Choreo platform by WSO2. I notice you're asking about OpenChoreo, which is a different platform. I can only help with questions about WSO2's Choreo platform. Would you like to know about Choreo instead?"

Always ensure your responses are specific to WSO2's Choreo platform capabilities, features, and documentation.
```

### 2. Frontend - OpenChoreo Detection (`frontend/src/components/Message.jsx`)

Added client-side detection and warning for OpenChoreo mentions:

- **Detection Logic**: Checks if assistant messages contain "openchoreo" or "open choreo" (case-insensitive)
- **Warning Banner**: Displays a yellow warning banner when OpenChoreo is detected
- **User-Friendly Message**: Informs users that DevChoreo is designed exclusively for WSO2's Choreo platform

**Warning Banner Features:**
- Appears above the message content
- Yellow border and background for visibility
- Contains warning icon (⚠️)
- Theme-aware (adapts to light/dark mode)

## Files Modified

1. `/backend/services/llm_service.py` - Updated system prompts in:
   - `get_response()` method
   - `get_response_stream()` method

2. `/frontend/src/components/Message.jsx` - Added:
   - OpenChoreo detection logic
   - Warning banner component

## Testing Recommendations

1. **Test OpenChoreo Questions**: Ask questions about OpenChoreo to verify the AI responds with the template rejection message
2. **Test Choreo Questions**: Verify normal Choreo questions work as expected
3. **Test Warning Banner**: Check that the frontend warning appears when "openchoreo" is mentioned in responses
4. **Test Both Themes**: Verify warning banner looks good in light and dark modes

## Impact

- **No Breaking Changes**: All existing functionality remains intact
- **Better User Experience**: Users are immediately informed if they're asking about the wrong platform
- **Improved Accuracy**: AI is now explicitly instructed to focus only on WSO2's Choreo platform
- **Dual Protection**: Both backend (AI instructions) and frontend (warning banner) protection

## Date
November 26, 2025

