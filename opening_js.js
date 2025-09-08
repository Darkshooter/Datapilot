// ----------------------------- MULTIPLE FILES ---------------------------------

// Global variables to store selected folder paths
let selectedInputFolder = "";
let selectedOutputFolder = "";

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

      // Check if both input and output folders are ready before enabling convert button
      checkAndEnableConvertButton();
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

// Function to validate output path and check if folders are ready
function validateOutputPath() {
  const outputInput = document.getElementById("output-folder-input");
  const statusDisplay = document.getElementById("output-folder-status");
  const outputPath = outputInput.value.trim();

  if (outputPath === "") {
    selectedOutputFolder = "";
    statusDisplay.innerHTML =
      "Enter the full path where you want to save the converted CSV files";
    statusDisplay.style.color = "#c4c4c4";
  } else if (isValidWindowsPath(outputPath)) {
    selectedOutputFolder = outputPath;
    statusDisplay.innerHTML = `✓ Output will be saved to: ${outputPath}`;
    statusDisplay.style.color = "#28a745";
  } else {
    selectedOutputFolder = "";
    statusDisplay.innerHTML =
      "❌ Please enter a valid Windows path (e.g., C:\\Users\\YourName\\Documents\\ConvertedFiles)";
    statusDisplay.style.color = "#ff2600";
  }

  // Check if both folders are ready
  checkAndEnableConvertButton();
}

// Function to validate Windows file path
function isValidWindowsPath(path) {
  // Basic Windows path validation
  const windowsPathRegex =
    /^[A-Za-z]:\\(?:[^<>:"/\\|?*\n\r]+\\)*[^<>:"/\\|?*\n\r]*$/;
  return windowsPathRegex.test(path) && path.length > 3;
}

// Function to check if both folders are selected and enable/disable convert button
function checkAndEnableConvertButton() {
  const convertButton = document.getElementById("btn-multiplefiles");

  if (selectedInputFolder && selectedOutputFolder) {
    convertButton.removeAttribute("disabled");
  } else {
    convertButton.setAttribute("disabled", "true");
  }
}

async function calculate_multiple_files() {
  /* Check if both input and output folders are selected */
  if (!selectedInputFolder) {
    alert("Please first select the folder containing your RXD files.");
    return;
  }

  if (!selectedOutputFolder) {
    alert("Please enter a valid output folder path.");
    return;
  }

  /* Start conversion with both folders */
  try {
    console.log("Starting conversion with:");
    console.log("Input folder:", selectedInputFolder);
    console.log("Output folder:", selectedOutputFolder);

    // Start conversion with both folders
    eel.convert_multiple_files(
      selectedInputFolder,
      selectedOutputFolder
    )(result_multiple_files);
  } catch (error) {
    console.error("Error starting conversion:", error);
    alert("Error starting conversion process. Please try again.");
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

  // Store output folder for success message before resetting
  const completedOutputFolder = selectedOutputFolder;

  // Reset input folder selection
  selectedInputFolder = "";
  const displayElement = document.getElementById("input-folder-display");
  displayElement.innerHTML = "No RXD files folder selected yet";
  displayElement.style.color = "#c4c4c4";
  displayElement.style.borderColor = "#1a2b353d";
  displayElement.style.backgroundColor = "transparent";

  // Reset output folder selection
  selectedOutputFolder = "";
  const outputInput = document.getElementById("output-folder-input");
  const outputStatus = document.getElementById("output-folder-status");
  outputInput.value = "";
  outputStatus.innerHTML =
    "Enter the full path where you want to save the converted CSV files";
  outputStatus.style.color = "#c4c4c4";

  // Disable the convert button since no folders are selected
  button.setAttribute("disabled", "true");

  if (result && result !== "empty") {
    showSuccessNotification(
      `Process Successful! CSV files have been saved to: ${completedOutputFolder}`
    );
  } else if (result === "empty") {
    alert(
      "Please make sure both input and output folders are specified before converting."
    );
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
    showErrorToast("Please connect your Logger to format");
  } else {
    // Show success toast for successful formatting
    showSuccessNotification("Format Logger process completed successfully!");
  }
}

// ----------------------------- EXTRACT DATA ----------------------------

function extractdata() {
  eel.extract_data()(extract_return);
}

// ----------------------------- SET DATE TIME ----------------------------

function setDateTime() {
  console.log("Set Date Time button clicked!");

  // First test eel communication
  console.log("Testing eel communication...");
  eel.test_debug()((result) => {
    console.log("Test function result:", result);
  });

  // Then call the actual function
  eel.set_date_time()(setDateTimeResult);
}

function formatTimeForUser(timeString) {
  // Convert "2024-01-15 14:30:25" to "Jan 15, 2024 at 2:30 PM"
  try {
    const date = new Date(timeString);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  } catch (e) {
    return timeString; // Fallback to original format
  }
}

function getCurrentPCTime() {
  // Get current PC time in the same format
  const now = new Date();
  return now.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function setDateTimeResult(result) {
  console.log("Backend response:", result);
  console.log("Return message:", result);

  // Check for detailed debug information in error messages
  if (result && result.includes("Debug information:")) {
    console.log("=== DETAILED DEBUG INFORMATION ===");

    // Split the debug message by the delimiter used in Python
    const debugParts = result.split(" | ");
    debugParts.forEach((part, index) => {
      console.log(`${index + 1}. ${part.trim()}`);
    });

    console.log("===================================");

    // Also log raw message for complete context
    console.log("Raw debug message:", result);
  }

  if (result === "not connected") {
    showErrorToast("ReXgen device not connected");
  } else if (result === "Date time set successfully") {
    const pcTime = getCurrentPCTime();
    showSuccessNotification(`Device time set to ${pcTime}`);
  } else if (result === "Date time set successfully (CLI method)") {
    const pcTime = getCurrentPCTime();
    showSuccessNotification(`Device time set to ${pcTime}`);
  } else if (result.startsWith("Device time set and verified:")) {
    const pcTime = getCurrentPCTime();
    showSuccessNotification(`Device time set to ${pcTime}`);
  } else if (result.startsWith("Time set but verification uncertain:")) {
    const pcTime = getCurrentPCTime();
    showSuccessNotification(`Device time set to ${pcTime}`);
  } else if (result === "Time set but could not verify") {
    const pcTime = getCurrentPCTime();
    showSuccessNotification(`Device time set to ${pcTime}`);
  } else if (result === "Device not ready") {
    showErrorToast("ReXgen device not ready for time setting");
  } else if (result === "Failed to set device time") {
    showErrorToast("Failed to set device time");
  } else if (result === "CLI method failed") {
    showErrorToast("Command line method failed to set time");
  } else if (
    result === "DLL file not found" ||
    (result && result.includes("DLL file not found"))
  ) {
    console.log(
      "DLL ERROR DETECTED - Check console for detailed debug information above"
    );
    showErrorToast(
      "RgUSBdrv.dll not found - Check browser console (F12) for detailed debug info"
    );
  } else if (result && result.includes("Device DLL not found")) {
    console.log(
      "DEVICE DLL ERROR DETECTED - Check console for detailed debug information above"
    );
    showErrorToast(
      "Device DLL not found - Check browser console (F12) for detailed debug info"
    );
  } else if (result === "32-bit helper script not found") {
    console.log("32-BIT SCRIPT ERROR DETECTED");
    showErrorToast(
      "32-bit helper script missing - check set_device_time_32bit.py"
    );
  } else if (result.includes("Architecture mismatch")) {
    console.log("ARCHITECTURE MISMATCH ERROR:", result);
    showErrorToast("Python/DLL architecture mismatch - need 32-bit Python");
  } else if (result.startsWith("DLL loading failed")) {
    console.log("DLL LOADING ERROR:", result);
    showErrorToast(result);
  } else if (result.startsWith("Could not run 32-bit Python script")) {
    console.log("32-BIT PYTHON ERROR:", result);
    showErrorToast("Install 32-bit Python: py -32 or python32 command needed");
  } else if (result.startsWith("Python execution error (103)")) {
    console.log("PYTHON EXECUTION ERROR 103:", result);
    showErrorToast(
      "Python execution failed - check 32-bit Python installation"
    );
  } else if (result.startsWith("Script failed (exit")) {
    console.log("SCRIPT EXIT ERROR:", result);
    showErrorToast(`Script execution error: ${result}`);
  } else if (result.startsWith("Error:")) {
    console.log("GENERAL ERROR:", result);
    showErrorToast(result);
  } else {
    const pcTime = getCurrentPCTime();
    showSuccessNotification(`Device time set to ${pcTime}`);
  }
}

// Add event listener for Set Date Time button
document
  .getElementById("set-date-time-btn")
  .addEventListener("click", function () {
    console.log("Set Date Time button clicked!");
    setDateTime();
  });
