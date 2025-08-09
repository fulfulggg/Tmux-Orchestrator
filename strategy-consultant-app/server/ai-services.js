const axios = require('axios');

// OpenAI API client
const openaiClient = axios.create({
  baseURL: 'https://api.openai.com/v1',
  headers: {
    'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
    'Content-Type': 'application/json',
  },
});

// Anthropic API client
const anthropicClient = axios.create({
  baseURL: 'https://api.anthropic.com/v1',
  headers: {
    'x-api-key': process.env.ANTHROPIC_API_KEY,
    'Content-Type': 'application/json',
    'anthropic-version': '2023-06-01',
  },
});

// Google Gemini API client
const geminiClient = axios.create({
  baseURL: 'https://generativelanguage.googleapis.com/v1beta',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Claude API call
async function callClaude(prompt) {
  try {
    if (!process.env.ANTHROPIC_API_KEY) {
      return { error: 'Anthropic API key not configured' };
    }

    const response = await anthropicClient.post('/messages', {
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1000,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    });

    return {
      feedback: response.data.content[0].text,
      model: 'Claude 3.5 Sonnet'
    };
  } catch (error) {
    console.error('Claude API error:', error.response?.data || error.message);
    return { 
      error: 'Claude API error',
      feedback: 'Claude APIの呼び出しでエラーが発生しました'
    };
  }
}

// OpenAI API call
async function callOpenAI(prompt) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      return { error: 'OpenAI API key not configured' };
    }

    const response = await openaiClient.post('/chat/completions', {
      model: 'gpt-4',
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ],
      max_tokens: 1000,
      temperature: 0.7,
    });

    return {
      feedback: response.data.choices[0].message.content,
      model: 'GPT-4'
    };
  } catch (error) {
    console.error('OpenAI API error:', error.response?.data || error.message);
    return { 
      error: 'OpenAI API error',
      feedback: 'OpenAI APIの呼び出しでエラーが発生しました'
    };
  }
}

// Google Gemini API call
async function callGemini(prompt) {
  try {
    if (!process.env.GOOGLE_API_KEY) {
      return { error: 'Google API key not configured' };
    }

    const response = await geminiClient.post(
      `/models/gemini-pro:generateContent?key=${process.env.GOOGLE_API_KEY}`,
      {
        contents: [{
          parts: [{
            text: prompt
          }]
        }]
      }
    );

    return {
      feedback: response.data.candidates[0].content.parts[0].text,
      model: 'Gemini Pro'
    };
  } catch (error) {
    console.error('Gemini API error:', error.response?.data || error.message);
    return { 
      error: 'Gemini API error',
      feedback: 'Gemini APIの呼び出しでエラーが発生しました'
    };
  }
}

// AI相互検証機能
async function verifyArgumentWithAI(argument) {
  const prompt = `
戦略コンサルティングの論点設計を検証してください。以下の観点から評価してください：

【論点情報】
大論点: ${argument.major_point}
中論点: ${argument.medium_point}
小論点: ${argument.minor_point}
仮説: ${argument.hypothesis}
検証アプローチ: ${argument.verification_approach}

【評価観点】
1. MECE性: 論点が漏れなく重複なく設計されているか
2. ロジカル性: 論点の階層構造が論理的に整合しているか
3. 具体性: クライアント固有の課題にフォーカスしているか
4. 実行可能性: 検証アプローチが現実的で実行可能か
5. 優先度: ビジネスインパクトの観点から重要度は適切か

簡潔に評価結果をお答えください（200文字以内）。
`;

  try {
    // 3つのAIモデルを並列で呼び出し
    const [claudeResult, openaiResult, geminiResult] = await Promise.all([
      callClaude(prompt),
      callOpenAI(prompt),
      callGemini(prompt)
    ]);

    // 合意レベルを計算（エラーがない応答の数）
    const validResponses = [claudeResult, openaiResult, geminiResult].filter(
      result => !result.error
    );
    const consensus = validResponses.length;

    // 総合評価を生成
    let overallFeedback;
    if (consensus === 3) {
      overallFeedback = "✅ 全モデル合意: 高品質な論点設計です。";
    } else if (consensus === 2) {
      overallFeedback = "⚠️ 多数決で採用: 一部改善の余地があります。";
    } else if (consensus === 1) {
      overallFeedback = "🔴 要検討: 論点設計の見直しが必要です。";
    } else {
      overallFeedback = "❌ API接続エラー: 検証を再実行してください。";
    }

    return {
      claude_feedback: claudeResult.feedback || 'エラーにより取得できませんでした',
      openai_feedback: openaiResult.feedback || 'エラーにより取得できませんでした',
      gemini_feedback: geminiResult.feedback || 'エラーにより取得できませんでした',
      consensus,
      overall_feedback: overallFeedback
    };

  } catch (error) {
    console.error('AI verification error:', error);
    return {
      claude_feedback: 'システムエラーが発生しました',
      openai_feedback: 'システムエラーが発生しました', 
      gemini_feedback: 'システムエラーが発生しました',
      consensus: 0,
      overall_feedback: '❌ システムエラー: しばらく時間をおいて再試行してください。'
    };
  }
}

module.exports = {
  verifyArgumentWithAI,
  callClaude,
  callOpenAI,
  callGemini
};