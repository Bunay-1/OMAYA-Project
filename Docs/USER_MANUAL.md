# OMAYA Platform - User Manual

## Table of Contents

- [Getting Started](#getting-started)
- [Dashboard Overview](#dashboard-overview)
- [Machine Monitoring](#machine-monitoring)
- [Telemetry Analysis](#telemetry-analysis)
- [Predictive Maintenance](#predictive-maintenance)
- [Alert Management](#alert-management)
- [Maintenance Scheduling](#maintenance-scheduling)
- [Data Interpretation Guide](#data-interpretation-guide)
- [Common Tasks](#common-tasks)
- [Best Practices](#best-practices)

---

## Getting Started

### Welcome to OMAYA Platform

The OMAYA Platform is an enterprise-grade monitoring system for industrial machine fleets. This manual will guide you through using the platform to monitor machines, analyze data, manage alerts, and schedule maintenance.

### System Requirements

- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Screen Resolution**: 1920x1080 or higher recommended
- **Internet Connection**: Stable connection for real-time updates
- **Permissions**: User account with appropriate access level

### First Login

1. **Access the Platform**
   - Open your browser and navigate to your platform URL
   - Default URL: `http://your-platform-url.com`

2. **Enter Credentials**
   - Username: Provided by your administrator
   - Password: Provided by your administrator
   - Click "Login"

3. **Change Password (First Time)**
   - You will be prompted to change your password on first login
   - Enter your new password (minimum 12 characters)
   - Confirm the password
   - Click "Change Password"

### User Interface Overview

The platform interface consists of:

- **Sidebar Navigation**: Left panel with module navigation
- **Main Content Area**: Center panel displaying current module content
- **Header**: Top bar with user information and settings
- **Status Bar**: Bottom bar showing system status and connection

### Navigation

#### Using the Sidebar

The sidebar provides quick access to all platform modules:

- **Overview**: Dashboard with fleet-wide metrics
- **Machines**: List and details of all machines
- **Telemetry**: Real-time sensor data streams
- **Predictive**: AI-powered maintenance predictions
- **Tools**: Tool lifecycle tracking
- **Alerts**: Alert management center
- **Maintenance**: Maintenance calendar and scheduling
- **Explainability**: AI model explanations
- **GraphQL**: Advanced data querying
- **Analytics**: Performance analytics
- **Audit**: System audit trails
- **Multi-Region**: Multi-region status
- **Settings**: User and system settings

#### Keyboard Shortcuts

- `Ctrl + K`: Quick search
- `Ctrl + B`: Toggle sidebar
- `Ctrl + R`: Refresh data
- `Esc`: Close panels/modals
- `F11`: Fullscreen mode

---

## Dashboard Overview

### Overview Tab

The Overview tab provides a comprehensive view of your entire machine fleet.

#### Key Performance Indicators (KPIs)

The top section displays six key metrics:

1. **OEE (Overall Equipment Effectiveness)**
   - **What it measures**: Overall equipment efficiency (0-100%)
   - **Good range**: 85%+
   - **Warning range**: 70-85%
   - **Critical range**: <70%
   - **How to interpret**: Higher is better. Indicates overall equipment performance

2. **Uptime**
   - **What it measures**: Percentage of time machines are operational
   - **Good range**: 95%+
   - **Warning range**: 90-95%
   - **Critical range**: <90%
   - **How to interpret**: Higher is better. Shows machine availability

3. **Defect Rate**
   - **What it measures**: Percentage of defective parts produced
   - **Good range**: <2%
   - **Warning range**: 2-5%
   - **Critical range**: >5%
   - **How to interpret**: Lower is better. Indicates production quality

4. **Throughput**
   - **What it measures**: Parts produced per hour
   - **Good range**: Depends on machine type
   - **How to interpret**: Compare against target throughput

5. **MTBF (Mean Time Between Failures)**
   - **What it measures**: Average time between machine failures (hours)
   - **Good range**: 100+ hours
   - **Warning range**: 50-100 hours
   - **Critical range**: <50 hours
   - **How to interpret**: Higher is better. Indicates reliability

6. **MTTR (Mean Time To Repair)**
   - **What it measures**: Average time to repair machines (hours)
   - **Good range**: <4 hours
   - **Warning range**: 4-8 hours
   - **Critical range**: >8 hours
   - **How to interpret**: Lower is better. Indicates repair efficiency

#### Fleet Overview Grid

The main area displays all machines in a grid view:

**Machine Card Information**:
- **Machine ID**: Unique identifier (e.g., M001)
- **Machine Name**: Descriptive name (e.g., OMAYA-5X #1)
- **Zone**: Production zone location
- **Status**: Current operational status
  - 🟢 **Green**: Operational
  - 🟡 **Yellow**: Warning
  - 🔴 **Red**: Critical/Error
  - ⚪ **Gray**: Offline/Maintenance
- **Key Metrics**: Current spindle speed, temperature, vibration
- **Last Update**: Timestamp of last data update

**Interacting with Machine Cards**:
- **Click**: Open detailed machine information panel
- **Hover**: View additional quick metrics
- **Right-click**: Context menu with quick actions

#### View Options

**Grid View**: Default view showing machines in a grid layout
- Best for: Overview of many machines
- Shows: Status, key metrics, quick information

**List View**: Detailed list view with sortable columns
- Best for: Detailed analysis and comparison
- Shows: All metrics, sortable columns

**Toggle Views**: Use the view toggle button in the top-right corner

#### Real-Time Updates

The dashboard updates every 3 seconds by default.

**Live/Pause Toggle**:
- **Live Mode**: Automatic updates every 3 seconds
- **Paused Mode**: Updates stopped, manual refresh required
- **Use Live Mode**: For real-time monitoring
- **Use Paused Mode**: For detailed analysis without data changing

---

## Machine Monitoring

### Machines Tab

The Machines tab provides detailed information about individual machines.

### Machine List

**Filtering**:
- **By Zone**: Select specific production zone
- **By Status**: Filter by operational status
- **By Machine Type**: Filter by machine type
- **Search**: Search by machine ID or name

**Sorting**:
- Click column headers to sort
- Sort by: ID, Name, Zone, Status, Temperature, Vibration, etc.

### Machine Detail Panel

When you click on a machine, the detail panel opens on the right side.

#### Machine Information Section

**Basic Information**:
- **Machine ID**: Unique identifier
- **Name**: Machine name
- **Zone**: Production zone
- **Status**: Current status
- **Manufacturer**: Equipment manufacturer
- **Model**: Machine model
- **Year**: Manufacturing year

**Specifications**:
- **Spindle Max RPM**: Maximum spindle speed
- **Axis Count**: Number of axes
- **Power Rating**: Power consumption
- **Work Area**: Working dimensions

#### Current State Section

**Real-Time Metrics**:
- **Spindle Speed**: Current RPM (revolutions per minute)
  - **Normal**: Within specified range for operation
  - **High**: Above normal operating range
  - **Low**: Below normal operating range

- **Temperature**: Current temperature (°C)
  - **Normal**: 20-60°C for most machines
  - **Warning**: 60-80°C
  - **Critical**: >80°C

- **Vibration**: Vibration level (mm/s)
  - **Normal**: <1.0 mm/s
  - **Warning**: 1.0-2.0 mm/s
  - **Critical**: >2.0 mm/s

- **Tool Wear**: Tool wear percentage
  - **Normal**: <70%
  - **Warning**: 70-85%
  - **Critical**: >85%

- **Cycle Time**: Current cycle time (seconds)
  - Compare against target cycle time
  - Longer cycle times indicate issues

- **Uptime**: Current uptime percentage
  - Higher is better
  - Indicates machine availability

#### Sensors Section

Lists all sensors connected to the machine:

**Sensor Information**:
- **Sensor ID**: Unique identifier
- **Type**: Sensor type (temperature, vibration, pressure, etc.)
- **Location**: Physical location on machine
- **Status**: Current sensor status
- **Current Value**: Current reading
- **Unit**: Measurement unit
- **Last Update**: Timestamp of last reading

**Sensor Status Indicators**:
- 🟢 **Active**: Sensor working normally
- 🟡 **Warning**: Sensor reading outside normal range
- 🔴 **Error**: Sensor malfunction
- ⚪ **Offline**: Sensor not responding

#### Historical Data Section

**Trend Charts**:
- **Temperature Trend**: Temperature over time
- **Vibration Trend**: Vibration over time
- **Performance Trend**: Overall performance metrics

**Chart Controls**:
- **Time Range**: Select time period (1h, 6h, 24h, 7d, 30d)
- **Zoom**: Click and drag to zoom
- **Pan**: Drag to pan
- **Reset**: Reset to default view

#### Maintenance Section

**Maintenance Information**:
- **Last Maintenance**: Date of last maintenance
- **Next Maintenance**: Scheduled next maintenance
- **Maintenance Type**: Preventive, corrective, or predictive
- **Assigned To**: Team or person responsible
- **Notes**: Maintenance notes and observations

#### Alert History Section

**Recent Alerts**:
- **Alert ID**: Unique identifier
- **Severity**: Info, Warning, Error, Critical
- **Type**: Alert type
- **Message**: Alert message
- **Timestamp**: When alert occurred
- **Status**: Active, acknowledged, resolved

### Machine Actions

**Quick Actions** (from detail panel):
- **Start Machine**: Start machine operation
- **Stop Machine**: Stop machine operation
- **Schedule Maintenance**: Schedule maintenance
- **View History**: View detailed history
- **Export Data**: Export machine data

**Context Menu** (right-click on machine):
- **View Details**: Open detail panel
- **Start**: Start machine
- **Stop**: Stop machine
- **Schedule Maintenance**: Schedule maintenance
- **View Alerts**: View machine alerts
- **Export Data**: Export data

---

## Telemetry Analysis

### Telemetry Tab

The Telemetry tab provides real-time sensor data streaming and analysis.

### Telemetry Feed

**Real-Time Event Stream**:
- Displays live sensor data updates
- Updates every 3 seconds in live mode
- Shows machine ID, sensor type, value, and timestamp

**Feed Controls**:
- **Live/Pause**: Toggle automatic updates
- **Auto-Scroll**: Automatically scroll to latest events
- **Clear**: Clear the feed
- **Export**: Export feed data

**Filtering**:
- **By Machine**: Filter by specific machine
- **By Sensor Type**: Filter by sensor type
- **By Value Range**: Filter by value range
- **By Time Range**: Filter by time period

### Interpreting Telemetry Data

#### Temperature Data

**Normal Ranges** (varies by machine type):
- **Spindle Bearings**: 30-50°C
- **Motor**: 40-60°C
- **Hydraulic System**: 35-55°C
- **Control Cabinet**: 20-40°C

**Interpretation**:
- **Stable**: Temperature within normal range, minimal fluctuation
- **Rising**: Temperature increasing over time - investigate
- **Fluctuating**: Rapid temperature changes - check cooling system
- **High**: Temperature above normal - risk of damage

#### Vibration Data

**Normal Ranges**:
- **Low Speed (<1000 RPM)**: <0.5 mm/s
- **Medium Speed (1000-3000 RPM)**: <1.0 mm/s
- **High Speed (>3000 RPM)**: <2.0 mm/s

**Interpretation**:
- **Stable**: Vibration within normal range
- **Increasing**: Vibration increasing - bearing wear or imbalance
- **Sudden Spike**: Immediate issue - check for damage
- **High**: Vibration above normal - risk of failure

#### Pressure Data

**Normal Ranges** (varies by system):
- **Hydraulic System**: 100-200 bar
- **Pneumatic System**: 6-8 bar
- **Cooling System**: 2-4 bar

**Interpretation**:
- **Stable**: Pressure within normal range
- **Low**: Pressure below normal - leak or pump issue
- **High**: Pressure above normal - blockage or regulator issue
- **Fluctuating**: Rapid changes - check for air in system

### Telemetry Charts

**Real-Time Charts**:
- **Temperature Chart**: Temperature over time
- **Vibration Chart**: Vibration over time
- **Pressure Chart**: Pressure over time
- **Multi-Sensor Chart**: Multiple sensors on one chart

**Chart Features**:
- **Real-time updates**: Live data streaming
- **Zoom**: Click and drag to zoom
- **Pan**: Drag to pan
- **Legend**: Click to toggle sensors
- **Export**: Export chart data

### Data Export

**Export Options**:
- **CSV**: Comma-separated values for Excel
- **JSON**: JSON format for data processing
- **PDF**: PDF report with charts

**Export Steps**:
1. Select time range
2. Select machines/sensors
3. Choose export format
4. Click "Export"
5. Download file

---

## Predictive Maintenance

### Predictive Tab

The Predictive tab provides AI-powered maintenance predictions and recommendations.

### Failure Probability

**Machine Failure Probability**:
- Displays probability of machine failure in next 48 hours
- **Low Risk**: <30% probability
- **Medium Risk**: 30-70% probability
- **High Risk**: >70% probability

**Interpretation**:
- **Low Risk**: Normal operation, continue monitoring
- **Medium Risk**: Increased risk, consider preventive maintenance
- **High Risk**: Immediate attention required, schedule maintenance

**Confidence Level**:
- Indicates how confident the AI model is in its prediction
- **High Confidence**: >85% - reliable prediction
- **Medium Confidence**: 70-85% - moderately reliable
- **Low Confidence**: <70% - prediction may be less accurate

### Remaining Useful Life (RUL)

**RUL Prediction**:
- Estimates remaining useful life in hours
- **Confidence Interval**: Range of possible values
- **Confidence**: Confidence level of prediction

**Interpretation**:
- **Long RUL** (>500 hours): Machine in good condition
- **Medium RUL** (200-500 hours): Plan maintenance in near future
- **Short RUL** (<200 hours): Schedule maintenance soon

### Risk Level Indicators

**Color Coding**:
- 🟢 **Green**: Low risk, normal operation
- 🟡 **Yellow**: Medium risk, monitor closely
- 🔴 **Red**: High risk, immediate attention

### Recommended Actions

The system provides specific recommendations:

**Examples**:
- "Schedule bearing inspection within 48 hours"
- "Check cooling system - temperature trending high"
- "Plan tool replacement - wear at 85%"
- "Inspect vibration dampeners - elevated readings"

**Following Recommendations**:
1. Review the recommendation
2. Check supporting data
3. Schedule appropriate action
4. Document action taken
5. Monitor results

### Model Performance

**Model Accuracy**:
- Displays current model accuracy
- Shows model version
- Indicates when model was last trained

**Model Drift**:
- Indicates if model performance is degrading
- Triggers model retraining if needed

---

## Alert Management

### Alerts Tab

The Alerts tab provides comprehensive alert management and notification.

### Alert List

**Alert Display**:
- **Severity**: Color-coded by severity
  - 🔴 **Critical**: Immediate attention required
  - 🟠 **Error**: Attention required
  - 🟡 **Warning**: Monitor closely
  - 🔵 **Info**: Informational

- **Machine**: Machine associated with alert
- **Type**: Alert type (temperature, vibration, etc.)
- **Message**: Alert message
- **Timestamp**: When alert occurred
- **Status**: Active, acknowledged, resolved

### Filtering Alerts

**Filter Options**:
- **By Severity**: Filter by severity level
- **By Machine**: Filter by specific machine
- **By Type**: Filter by alert type
- **By Status**: Filter by status
- **By Time Range**: Filter by time period

### Alert Actions

**Acknowledge Alert**:
- Indicates you have seen the alert
- Does not resolve the underlying issue
- Prevents alert from appearing in new alerts

**Resolve Alert**:
- Indicates the issue has been resolved
- Alert is removed from active alerts
- Requires resolution notes

**Escalate Alert**:
- Escalate to higher priority
- Assign to specific person/team
- Add escalation notes

### Alert Details

Click on an alert to view details:

**Alert Information**:
- **Alert ID**: Unique identifier
- **Severity**: Severity level
- **Machine**: Affected machine
- **Type**: Alert type
- **Title**: Alert title
- **Message**: Detailed message
- **Timestamp**: When alert occurred
- **Duration**: How long alert has been active

**Sensor Data**:
- Shows sensor readings that triggered alert
- Displays historical trend
- Shows threshold values

**Related Alerts**:
- Shows other related alerts
- Helps identify patterns

### Alert Notification

**Notification Methods**:
- **In-App**: Real-time in-app notifications
- **Email**: Email notifications
- **SMS**: SMS notifications (if configured)
- **Slack**: Slack notifications (if configured)

**Notification Settings**:
- Configure notification preferences in Settings
- Set notification rules by severity
- Set quiet hours

---

## Maintenance Scheduling

### Maintenance Tab

The Maintenance tab provides maintenance scheduling and tracking.

### Maintenance Calendar

**Calendar Views**:
- **Month View**: Monthly overview
- **Week View**: Weekly detailed view
- **Day View**: Daily detailed view

**Maintenance Events**:
- **Preventive**: Scheduled preventive maintenance
- **Corrective**: Unplanned corrective maintenance
- **Predictive**: AI-predicted maintenance

**Color Coding**:
- 🟢 **Preventive**: Green - scheduled maintenance
- 🟡 **Corrective**: Yellow - corrective maintenance
- 🔴 **Predictive**: Red - urgent predictive maintenance

### Scheduling Maintenance

**Create New Maintenance Event**:
1. Click "Schedule Maintenance" button
2. Select machine
3. Select maintenance type
4. Select date and time
5. Set estimated duration
6. Assign team/person
7. Add description and notes
8. Click "Schedule"

**Drag and Drop**:
- Drag maintenance events to reschedule
- Conflicts are highlighted
- Overlap warnings displayed

### Maintenance Details

**Event Information**:
- **Event ID**: Unique identifier
- **Machine**: Machine for maintenance
- **Type**: Maintenance type
- **Scheduled Date**: Scheduled date/time
- **Estimated Duration**: Estimated time required
- **Assigned To**: Team or person
- **Status**: Scheduled, in progress, completed
- **Description**: Maintenance description
- **Notes**: Additional notes

### Maintenance Actions

**Start Maintenance**:
- Mark maintenance as in progress
- Records start time
- Notifies assigned team

**Complete Maintenance**:
- Mark maintenance as completed
- Records completion time
- Requires completion notes
- Updates machine status

**Cancel Maintenance**:
- Cancel scheduled maintenance
- Requires cancellation reason
- Notifies assigned team

### Maintenance History

**View History**:
- Filter by machine
- Filter by date range
- Filter by maintenance type
- Export history report

---

## Data Interpretation Guide

### Understanding Metrics

#### OEE (Overall Equipment Effectiveness)

**Formula**: OEE = Availability × Performance × Quality

**Components**:
- **Availability**: Percentage of planned production time
- **Performance**: Speed at which operations run compared to standard
- **Quality**: Percentage of good parts produced

**Interpretation**:
- **World Class**: 85%+
- **Good**: 60-85%
- **Typical**: 40-60%
- **Poor**: <40%

**Improvement Strategies**:
- **Low Availability**: Reduce downtime, improve maintenance
- **Low Performance**: Optimize cycle times, reduce minor stops
- **Low Quality**: Reduce defects, improve process control

#### Temperature

**Normal Operating Ranges**:
- **Spindle**: 30-50°C
- **Motor**: 40-60°C
- **Hydraulic**: 35-55°C
- **Electronics**: 20-40°C

**Warning Signs**:
- **Gradual Increase**: Worn bearings, cooling issues
- **Sudden Spike**: Immediate failure risk
- **Fluctuation**: Sensor or cooling system issues

#### Vibration

**Severity Levels**:
- **Good**: <0.5 mm/s
- **Satisfactory**: 0.5-1.0 mm/s
- **Monitor**: 1.0-2.0 mm/s
- **Unsatisfactory**: 2.0-4.0 mm/s
- **Critical**: >4.0 mm/s

**Frequency Analysis**:
- **Low Frequency (<10 Hz)**: Imbalance, misalignment
- **Medium Frequency (10-1000 Hz)**: Bearing wear
- **High Frequency (>1000 Hz)**: Gear issues, lubrication

#### Tool Wear

**Wear Stages**:
- **Initial (0-30%)**: New tool, optimal performance
- **Normal (30-70%)**: Normal wear, consistent performance
- **Warning (70-85%)**: Increased wear, monitor closely
- **Critical (85-100%)**: Replace tool immediately

**Replacement Indicators**:
- Wear percentage >85%
- Surface finish degradation
- Dimensional errors
- Increased cutting forces

### Trend Analysis

#### Identifying Trends

**Upward Trends**:
- Gradual increase over time
- Indicates degradation
- Plan preventive action

**Downward Trends**:
- Gradual decrease over time
- May indicate improvement or sensor issue
- Verify with other metrics

**Cyclic Patterns**:
- Regular repeating patterns
- May indicate process cycles
- Normal for some operations

**Sudden Changes**:
- Abrupt changes in values
- Immediate investigation required
- Check for equipment issues

#### Statistical Analysis

**Mean (Average)**:
- Central tendency of data
- Compare against target values

**Standard Deviation**:
- Measure of variability
- High deviation indicates instability

**Control Limits**:
- Upper Control Limit (UCL): Mean + 3σ
- Lower Control Limit (LCL): Mean - 3σ
- Values outside limits indicate special causes

### Correlation Analysis

**Finding Relationships**:
- Compare multiple metrics
- Identify correlations
- Understand cause-effect relationships

**Common Correlations**:
- **Temperature vs. Vibration**: Higher temperature often correlates with higher vibration
- **Tool Wear vs. Quality**: Increased wear often correlates with decreased quality
- **Cycle Time vs. Temperature**: Longer cycles may indicate thermal issues

---

## Common Tasks

### Daily Monitoring Routine

**Morning Check**:
1. Log into platform
2. Review Overview tab for fleet status
3. Check critical alerts
4. Review machines with warnings
5. Note any machines requiring attention

**Throughout Day**:
1. Monitor telemetry feed
2. Watch for new alerts
3. Check machine performance
4. Review predictive maintenance recommendations

**End of Day**:
1. Review daily performance
2. Document any issues
3. Plan next day's priorities
4. Ensure all alerts acknowledged

### Responding to Critical Alerts

**Immediate Actions**:
1. Acknowledge the alert
2. Review alert details
3. Check machine status
4. Assess severity
5. Take appropriate action

**Action Steps**:
1. **Stop Machine**: If immediate risk
2. **Inspect Machine**: Visual inspection
3. **Check Sensors**: Verify sensor readings
4. **Consult Team**: Get expert opinion
5. **Document**: Record actions taken

### Scheduling Maintenance

**Preventive Maintenance**:
1. Review machine status
2. Check predictive recommendations
3. Schedule appropriate time
4. Assign team
5. Prepare parts and tools
6. Document plan

**Corrective Maintenance**:
1. Identify issue
2. Assess urgency
3. Schedule as soon as possible
4. Assign team
5. Prepare parts
6. Document cause

### Analyzing Performance

**Weekly Analysis**:
1. Review OEE trends
2. Analyze machine performance
3. Identify underperforming machines
4. Review maintenance effectiveness
5. Plan improvements

**Monthly Analysis**:
1. Review fleet-wide performance
2. Analyze trends over time
3. Compare against targets
4. Identify improvement opportunities
5. Update maintenance schedules

---

## Best Practices

### Data Monitoring

**Regular Monitoring**:
- Check dashboard at least daily
- Review critical alerts immediately
- Monitor trends over time
- Compare against baselines

**Focus on Trends**:
- Look for gradual changes
- Identify patterns
- Correlate with events
- Predict future issues

### Alert Management

**Timely Response**:
- Acknowledge alerts promptly
- Investigate root causes
- Take appropriate action
- Document resolutions

**Prioritization**:
- Critical alerts first
- Error alerts second
- Warning alerts as time permits
- Info alerts for information

### Maintenance Planning

**Proactive Approach**:
- Use predictive maintenance
- Schedule preventive maintenance
- Plan for wear items
- Maintain spare parts inventory

**Documentation**:
- Document all maintenance
- Record root causes
- Track effectiveness
- Update procedures

### Data Interpretation

**Context Matters**:
- Consider operating conditions
- Account for machine type
- Compare with historical data
- Understand normal variations

**Multiple Metrics**:
- Don't rely on single metric
- Correlate multiple indicators
- Look for patterns
- Verify with physical inspection

### Continuous Improvement

**Learn from Data**:
- Analyze failures
- Identify patterns
- Improve processes
- Update procedures

**Share Knowledge**:
- Document lessons learned
- Train team members
- Share best practices
- Continuously improve

---

## Getting Help

### In-App Help

- **Help Button**: Click help icon (?) in top-right corner
- **Tooltips**: Hover over elements for tooltips
- **Context Help**: Click help icons on specific pages

### Support Resources

- **User Manual**: This document
- **Training Videos**: Available in platform
- **Knowledge Base**: Online knowledge base
- **Support Team**: Contact support for assistance

### Contact Information

- **Email**: support@omaya-platform.com
- **Phone**: +1-555-OMAYA-HELP
- **Chat**: In-app chat support
- **Portal**: support.omaya-platform.com

---

**Version**: 3.1.0
**Last Updated**: June 2026
