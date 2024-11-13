// ----------------------------- MULTIPLE FILES ---------------------------------

function calculate_multiple_files() {
  /* get inputs from widgets */
  input = document.getElementById("input-multiple");
  output = document.getElementById("output-multiple");
  // raster_rate = document.getElementById("raster-multiple");

  eel.convert_multiple_files(input.value, output.value)(result_multiple_files);
}

document
  .getElementById("btn-multiplefiles")
  .addEventListener("click", function () {
    this.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Converting...';
    this.setAttribute("disabled", "true");
  });

function result_multiple_files(result) {
  button = document.getElementById("btn-multiplefiles");
  button.innerHTML = "Convert Files";
  button.removeAttribute("disabled");

  document.getElementById("input-multiple").value = "";
  document.getElementById("output-multiple").value = "";
  // document.getElementById("raster-multiple").value="";

  console.log(result);
  // message.innerHTML = result;
}

// ----------------------------- SINGLE FILE ----------------------------

function getPathToFile() {
  output = document.getElementById("output-single");
  // raster_rate = document.getElementById("raster_single");

  eel.pythonFunction(output.value)(result_single_file);
}

document
  .getElementById("convert-single")
  .addEventListener("click", function () {
    this.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Converting...';
    this.setAttribute("disabled", "true");
  });

function result_single_file(result) {
  button = document.getElementById("convert-single");
  button.innerHTML = "Upload & Convert";
  button.removeAttribute("disabled");

  document.getElementById("output-single").value = "";
  // document.getElementById("raster_single").value="";
  console.log(result);
  // message.innerHTML = result;
}

// ----------------------------- SETUP LOGGER ----------------------------

function setuplogger_fnc() {
  document.getElementById("not-connected").innerHTML = "";

  var checkbox_two = document.getElementById("format");

  var format_logger = checkbox_two.checked;

  console.log(format_logger);

  eel.setup_logger(format_logger)(setup_return);
}

document.getElementById("setuplogger").addEventListener("click", function () {
  this.innerHTML =
    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Setting Logger...';
  this.setAttribute("disabled", "true");
});

function setup_return(msg) {
  if (msg === "not connected") {
    button = document.getElementById("setuplogger");
    button.innerHTML = "Setup Logger";
    button.removeAttribute("disabled");

    document.getElementById("not-connected").innerHTML =
      '<i class = "fas fa-solid fa-circle-xmark fa-2x" id="icon-nc"></i> ReXgen Logger is not connected to your computer';
  } else {
    button = document.getElementById("setuplogger");
    button.innerHTML = "Setup Logger";
    button.removeAttribute("disabled");
    document.getElementById("not-connected2").innerHTML = "Process Successful!";
  }

  // message.innerHTML = result;
}

// ----------------------------- EXTRACT DATA ----------------------------

function extractdata() {
  eel.extract_data()(extract_return);
}
