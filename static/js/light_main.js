$(function () {
  const openModalBtn = document.getElementById("openAzureModal");
  const modal = document.getElementById("azureTranslateContainer");
  const overlay = document.getElementById("azureTranslateModalOverlay");
  const closeModalBtn = document.getElementById("closeAzureModal");

  function showModal() {
    modal.style.display = "flex";
    overlay.style.display = "block";
  }

  function hideModal() {
    modal.style.display = "none";
    overlay.style.display = "none";
  }

  openModalBtn.addEventListener("click", showModal);
  closeModalBtn.addEventListener("click", hideModal);
  overlay.addEventListener("click", hideModal);

  socket.on("light_state", function (data) {
    state = data.state;
    toggleLampadario(state, data.inputValue);
    moodCheckOut(state);
  });

  $("#submit").click(light);
  $("#message").keypress(function (e) {
    if (e.which == 13) {
      light();
    }
  });

  $("#lampadario").click(function () {
    $("#input_data").empty();
    $("#footer").empty();
    $("#shadow").empty();
    socket.emit("toggle_light_state");
  });

  langs.forEach(function (lang) {
    $("#azureTranslateAudioVoice" + lang).click(function () {
      var $audio = $("#azureTranslateAudio" + lang);
      lang_name = lang === "Zh-Hant" ? "zh-Hant" : lang;
      $audio.attr("src", "");
      $audio.attr(
        "src",
        audioUrl + "/speech_" + lang_name + ".mp3?a=" + Math.random()
      );
      $audio[0].load();
      $audio[0].play();
    });
  });
});

function setMood(mood) {
  document
    .querySelectorAll(".bg-gradient")
    .forEach((el) => el.classList.remove("active"));
  document.querySelector(".bg-gradient." + mood).classList.add("active");
}

function moodCheckOut(
  state = "開",
  sentiment = "neutral",
  sentiment_score = 1,
  emotion = "平靜"
) {
  if (sentiment !== undefined && sentiment !== null) {
    document.getElementById(sentiment).checked = true;
    sentiment_score = state === "關" ? 0 : sentiment_score;
    let alpha = Math.min(Math.max(sentiment_score, 0.3), 1); // 限制在 0.2~1 之間
    animateLampGlow(alpha, state);
    const labelMap = {
      positive: emotion + "（萌葱色）",
      neutral: emotion + "（白練）",
      negative: emotion + "（濃藍）",
    };
    document.getElementById("moodText").textContent = labelMap[sentiment];
    document.getElementById("moodTextBox").style.opacity = "1";

    setMood(sentiment);
  }
}

// 情緒分析
function toggleLampadario(value, inputValue = "") {
  $("#input_data").text(inputValue);
  if (value === "開") {
    $("#lampadario_on").prop("checked", true);
    $("#lampadario_off").prop("checked", false);
  } else if (value === "關") {
    $("#lampadario_off").prop("checked", true);
    $("#lampadario_on").prop("checked", false);
  } else {
    $("#footer").text(value);
    $("#shadow").text(value);
  }
}

function light() {
  $("#input_data").empty();
  $("#footer").empty();
  $("#shadow").empty();

  var message = $("#message").val();
  var model_select = $("#model-select").val();
  var params = {
    message: message,
    model: model_select,
  };
  console.log(params);
  $.post(apiUrl + "/light", params, function (data) {
    console.log(data);
    toggleLampadario(data.entity, message);
    emotion = data.emotion["emotion"];
    state = data.entity;
    sentiment_score = Math.max(
      parseFloat(data.confidence_scores.neutral),
      parseFloat(data.confidence_scores.positive)
      // parseFloat(data.confidence_scores.negative)
    );

    moodCheckOut(state, data.sentiment, sentiment_score, emotion);
    console.log("state:", state);
    console.log("情緒分析結果:", data.sentiment);
    console.log("情緒分析分數:", data.confidence_scores);
    console.log("sentiment_score:", sentiment_score);

    if (!["開", "關"].includes(data.entity)) {
      azureTranslate(data.entity);
    }
  });
  $("#message").val("");
}

function animateLampGlow(alpha, state = "開") {
  let $label = $("#lampadario_box label");

  if (state === "關") {
    // 關燈：背景淡、光暈消失
    $label.css("background", "rgba(255,255,255,0.03)");
    $label.css(
      "box-shadow",
      "inset 0px 1px 5px rgba(255,255,255,0.1), inset 0px 2px 20px rgba(255,255,255,0.07), -80px -15px 15px -5px rgba(0,0,0,0.1)"
    );
  } else {
    // 先亮燈（背景變亮，光暈暫時設很小）
    $label.css("background", "rgba(255,255,255," + alpha + ")");
    $label.css("box-shadow", "0 0 2px rgba(255,255,255,0.1)");
    // 延遲後再展開光暈
    setTimeout(function () {
      $label.css(
        "box-shadow",
        "0 0 10px rgba(255,255,255," +
          alpha +
          "), " +
          "0 0 30px rgba(255,255,255," +
          alpha * 0.8 +
          "), " +
          "0 0 50px rgba(255,255,255," +
          alpha * 0.6 +
          ")"
      );
    }, 100); // 0.35秒後展開光暈
  }
}

function azureTranslate(message) {
  $("#azureTranslateText").empty();
  $("#azureTranslateContainer").hide();

  var params = {
    message: message,
  };
  $.post(apiUrl + "/azure_translate", params, function (data) {
    $("#azureTranslateText").html(data);
    $("#azureTranslateContainer").show();
  });
}
