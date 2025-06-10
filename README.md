# HiringAgent - AI-Powered Technical Interview System

An intelligent, automated interview system that conducts structured technical screenings with adaptive conversation flow, real-time question generation, and comprehensive candidate evaluation.
---
![Application Screenshot(Form Submission Page)](assets/ss_1.png)
---
![Application Screenshot(Chat Interface)](assets/ss_2.png)
---
## 🚀 Overview

The **HiringAgent** is a sophisticated AI interviewer that combines casual conversation with structured technical assessments. It dynamically generates personalized screening questions based on job descriptions and candidate profiles, then conducts fair, consistent interviews with built-in evaluation mechanisms.

## ✨ Key Features

### 🧠 **Intelligent Dual-LLM Architecture**
- **Primary LLM**: Gemini (default) for main interview operations
- **Fallback LLM**: Hyperbolic for redundancy and reliability
- Automatic failover ensures uninterrupted interview sessions

### 📋 **Multi-Phase Interview Flow**
1. **Casual Chat Phase**: Natural conversation while questions generate
2. **Structured Questions Phase**: Technical screening with strict fairness rules
3. **Post-Interview Phase**: Analysis and final recommendations

### 🎯 **Dynamic Question Generation**
- Asynchronous question generation based on JD requirements
- Personalized screening questions tailored to candidate profile
- Structured output with section categorization and difficulty levels

### 📊 **Comprehensive Evaluation System**
- Real-time response tracking and scoring
- Structured performance analysis with detailed feedback
- Final hiring recommendations with confidence ratings

### 🛡️ **Fairness & Integrity Controls**
- Strict interview rules enforcement
- No external assistance detection
- Consistent question presentation format
- Response length limitations (500 characters max)

### 🕒 **Session Management & Resource Controls***

- Time Limit: 3-minute maximum session duration with automatic timeout
- **Interaction Limit**: Maximum 15 chat interactions per session
- **Session Tracking**: Real-time elapsed time and interaction count monitoring
- **Automatic Restart**: Complete session reset on timeout or limit reached
- **Resource Protection**: Prevents excessive usage and ensures fair access

## 🏗️ System Architecture

### Core Components

```
HiringAgent
├── Interview Management
│   ├── Phase Controller (casual_chat → structured_questions → post_interview)
│   ├── Question Generator (async, JD-based)
│   └── Response Tracker
├── LLM Integration
│   ├── Primary/Fallback System
│   ├── Custom System Prompts
│   └── Tool Selection Logic
└── Evaluation Engine
    ├── Performance Analyzer
    ├── Score Calculator
    └── Report Generator
```

## 🔧 Installation & Setup

### Prerequisites
```bash
# Required environment variables
