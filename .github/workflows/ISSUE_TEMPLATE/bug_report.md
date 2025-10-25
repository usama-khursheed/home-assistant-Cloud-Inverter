---
name: Bug Report
about: Report a bug to help us improve the Cloud Inverter integration
title: "[BUG] "
labels: bug
assignees: usama-khursheed
---

 🐛 Describe the Bug
A clear and concise description of what the bug is.

 📍 Steps to Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

 ✅ Expected Behavior
A clear and concise description of what you expected to happen.

 🔴 Actual Behavior
What actually happened instead of the expected behavior.

 📸 Screenshots
If applicable, add screenshots or screen recordings to help explain your problem.

 🛠️ Environment Information
Please complete the following information:

- Home Assistant Version: [e.g., 2024.11.0, 2024.12.1]
- Integration Version: [e.g., 1.0.0]
- Inverter Model: [e.g., SM-ONYX-UL-6KW]
- Python Version: [e.g., 3.12]
- Operating System: [e.g., Raspberry Pi OS, Ubuntu, Windows]
- Installation Method: [e.g., HACS, Manual]

 📋 System Details
```
Please paste the output of the Home Assistant System Health page here:
Settings → System → System Health → Copy Information
```

 📝 Integration Diagnostic Data
To get diagnostic data:
1. Go to Settings → Devices & Services
2. Find Cloud Inverter integration
3. Click the three dots → Download diagnostics

Paste diagnostic file here (or key information):
```
{paste diagnostic data here}
```

 📜 Home Assistant Logs
To enable debug logging:
1. Add this to your `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.cloud_inverter: debug
```
2. Restart Home Assistant
3. Reproduce the issue
4. Go to Settings → System → Logs
5. Search for "cloud_inverter"
6. Copy the relevant logs

Paste logs here:
```
{paste logs here}
```

 🔍 Additional Context
Add any other context about the problem here. For example:
- When did this start happening? (e.g., after updating HA, after restarting integration)
- Does this happen consistently or intermittently?
- Are there any related issues or discussions?
- Have you tried restarting Home Assistant or reloading the integration?

 ✅ Troubleshooting Checklist
Please check these before submitting:
- [ ] I'm using the latest version of the integration
- [ ] I've checked the documentation (README.md, QUICKSTART.md)
- [ ] I've checked existing issues to see if this is already reported
- [ ] I've enabled debug logging and checked the logs
- [ ] I've tried restarting Home Assistant
- [ ] I've tried reloading the integration
- [ ] I've verified my CloudInverter.net credentials are correct

 📌 Workaround
If you've found a workaround, please describe it here:

 🎯 Priority
How critical is this bug?
- [ ] Blocking (Integration doesn't work at all)
- [ ] High (Major functionality broken)
- [ ] Medium (Some features not working)
- [ ] Low (Minor issue or edge case)

---

Thank you for helping improve the Cloud Inverter integration! 🙏

Note: Please provide as much detail as possible. Issues without sufficient information may be closed.
