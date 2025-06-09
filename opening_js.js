// ----------------------------- MULTIPLE FILES ---------------------------------

// Global variables to store selected folder paths
let selectedInputFolder = "";

// ----------------------------- SUCCESS NOTIFICATION ---------------------------------

function showSuccessNotification(message) {
  const container = document.getElementById("toast-container");

  // Create success notification
  const notification = document.createElement("div");
  notification.className = "success-toast";
  notification.innerHTML = `
    <button class="toast-close">&times;</button>
    <span class="icon">✓</span>${message}
  `;

  // Make entire toast clickable to close
  notification.addEventListener("click", function (e) {
    console.log("Toast clicked!"); // Debug log
    closeSuccessToast(notification);
  });

  // Add specific click event listener to close button (with event stopping)
  const closeButton = notification.querySelector(".toast-close");
  closeButton.addEventListener("click", function (e) {
    console.log("Close button clicked!"); // Debug log
    e.stopPropagation(); // Prevent event bubbling
    closeSuccessToast(notification);
  });

  // Add to container
  container.appendChild(notification);

  // Show animation
  setTimeout(() => {
    notification.classList.add("show");
  }, 100);
}

function showErrorToast(message) {
  const container = document.getElementById("toast-container");

  // Create error notification
  const notification = document.createElement("div");
  notification.className = "success-toast error-toast";
  notification.innerHTML = `
    <button class="toast-close">&times;</button>
    <span class="icon">❌</span>${message}
  `;

  // Make entire toast clickable to close
  notification.addEventListener("click", function (e) {
    console.log("Error toast clicked!"); // Debug log
    closeSuccessToast(notification);
  });

  // Add specific click event listener to close button (with event stopping)
  const closeButton = notification.querySelector(".toast-close");
  closeButton.addEventListener("click", function (e) {
    console.log("Close button clicked!"); // Debug log
    e.stopPropagation(); // Prevent event bubbling
    closeSuccessToast(notification);
  });

  // Add to container
  container.appendChild(notification);

  // Show animation
  setTimeout(() => {
    notification.classList.add("show");
  }, 100);
}

function closeSuccessToast(notification) {
  console.log("Closing toast..."); // Debug log
  notification.classList.remove("show");
  setTimeout(() => {
    if (notification.parentElement) {
      notification.parentElement.removeChild(notification);
      console.log("Toast removed!"); // Debug log
    }
  }, 300);
}

// Function to select input folder
async function selectInputFolder() {
  try {
    const folderPath = await eel.select_input_folder()();
    if (folderPath) {
      selectedInputFolder = folderPath;
      const displayElement = document.getElementById("input-folder-display");
      displayElement.innerHTML = `${folderPath}`;
      displayElement.style.color = "#c4c4c4";
      displayElement.style.borderColor = "#1a2b353d";
      displayElement.style.backgroundColor = "transparent";

      // Enable the convert button when folder is selected
      const convertButton = document.getElementById("btn-multiplefiles");
      convertButton.removeAttribute("disabled");
    }
  } catch (error) {
    console.error("Error selecting input folder:", error);
    const displayElement = document.getElementById("input-folder-display");
    displayElement.innerHTML = "❌ Error selecting RXD files folder";
    displayElement.style.color = "#ff2600";
    displayElement.style.borderColor = "#1a2b353d";
    displayElement.style.backgroundColor = "transparent";

    // Disable the convert button on error
    const convertButton = document.getElementById("btn-multiplefiles");
    convertButton.setAttribute("disabled", "true");
  }
}

async function calculate_multiple_files() {
  /* First check if input folder is selected */
  if (!selectedInputFolder) {
    alert("Please first select the folder containing your RXD files.");
    return;
  }

  /* Create automatic output folder */
  try {
    const outputFolder = await eel.create_automatic_output_folder(
      selectedInputFolder
    )();
    if (!outputFolder) {
      alert(
        "Error creating output folder on desktop. Please check permissions."
      );
      return;
    }

    // Start conversion with both folders
    eel.convert_multiple_files(
      selectedInputFolder,
      outputFolder
    )(result_multiple_files);
  } catch (error) {
    console.error("Error creating output folder:", error);
    alert("Error creating output folder on desktop. Please try again.");
  }
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

  // Reset input folder selection
  selectedInputFolder = "";
  const displayElement = document.getElementById("input-folder-display");
  displayElement.innerHTML = "No RXD files folder selected yet";
  displayElement.style.color = "#c4c4c4";
  displayElement.style.borderColor = "#1a2b353d";
  displayElement.style.backgroundColor = "transparent";

  // Disable the convert button since no folder is selected
  button.setAttribute("disabled", "true");

  if (result && result !== "empty") {
    showSuccessNotification(
      "Process Successful! Log files saved to the desktop folder called DataPilotFiles"
    );
  } else if (result === "empty") {
    alert("Please make sure the input folder is selected before converting.");
  }
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
  // Direct format logger without checkbox - always format
  var format_logger = true;

  console.log(format_logger);

  eel.setup_logger(format_logger)(setup_return);
}

document.getElementById("setuplogger").addEventListener("click", function () {
  this.innerHTML =
    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Formatting Logger...';
  this.setAttribute("disabled", "true");
});

function setup_return(msg) {
  button = document.getElementById("setuplogger");
  button.innerHTML = "Format Logger";
  button.removeAttribute("disabled");

  if (msg === "not connected") {
    // Show error toast for connection issue
    showErrorToast("❌ ReXgen Logger is not connected to your computer");
  } else {
    // Show success toast for successful formatting
    showSuccessNotification("Format Logger process completed successfully!");
  }
}

// ----------------------------- EXTRACT DATA ----------------------------

function extractdata() {
  eel.extract_data()(extract_return);
}
