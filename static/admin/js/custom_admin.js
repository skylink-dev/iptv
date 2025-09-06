document.addEventListener("DOMContentLoaded", function() {

  function addSelectButtonTo(container, appName, isOptgroup) {
    if (!container || container.dataset.hasSelectAll) return;

    // Create button
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm btn-primary permission-select-btn";
    btn.textContent = appName ? "Select All (" + appName + ")" : "Select All";

    // Placement
    if (isOptgroup) {
      // Insert button before the optgroup (safe placement)
      var wrapper = document.createElement("div");
      wrapper.className = "optgroup-select-wrapper";
      container.parentNode.insertBefore(wrapper, container);
      wrapper.appendChild(btn);
      wrapper.appendChild(container);
    } else {
      var label = container.querySelector("label") || container.querySelector(".field-label");
      if (label && label.parentNode) {
        label.parentNode.insertBefore(btn, label.nextSibling);
      } else {
        container.insertBefore(btn, container.firstChild);
      }
    }

    // Toggle logic
    btn.addEventListener("click", function () {
      var items = isOptgroup
        ? container.querySelectorAll("option")
        : container.querySelectorAll('input[type="checkbox"], option');

      if (!items.length) return;

      var allSelected = Array.prototype.every.call(items, function(el) {
        return el.selected || el.checked;
      });

      Array.prototype.forEach.call(items, function(el) {
        if ("checked" in el) {
          el.checked = !allSelected;
          el.dispatchEvent(new Event('change', { bubbles: true }));
        } else if ("selected" in el) {
          el.selected = !allSelected;
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });

      // Update button state
      btn.textContent = allSelected
        ? (appName ? "Select All ("+appName+")" : "Select All")
        : (appName ? "Unselect All ("+appName+")" : "Unselect All");

      btn.classList.toggle("btn-primary", allSelected);
      btn.classList.toggle("btn-warning", !allSelected);
    });

    container.dataset.hasSelectAll = "1";
  }

  // 🔹 Selectors (global containers)
  var selectors = [
    '.form-row.field-permissions',
    '.form-row.field-user_permissions',
    '#id_permissions',
    '#id_user_permissions'
  ];

  function init() {
    selectors.forEach(function(sel){
      document.querySelectorAll(sel).forEach(function(container) {
        addSelectButtonTo(container, null, false);

        // Per-app optgroups
        container.querySelectorAll("optgroup").forEach(function(optgroup) {
          var appName = optgroup.label;
          addSelectButtonTo(optgroup, appName, true);
        });
      });
    });
  }

  // Run initially
  init();

  // Watch for late-loaded DOM changes
  var observer = new MutationObserver(init);
  observer.observe(document.body, { childList: true, subtree: true });
});
