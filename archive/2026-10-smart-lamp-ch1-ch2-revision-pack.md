# Smart lamp thesis — Chapter 1 & 2 revision pack

**Prepared 2026-10-02.** Paste-ready replacement text for the Chapter 1 and Chapter 2 items left open by
`archive/2026-10-smart-lamp-revision-check.md`. Written against the 2.0 draft
(`archive/2026-10-smart-lamp-thesis-v2.md`) and the adviser's comments in 1.0
(`archive/2026-10-smart-lamp-thesis.md`).

**How to use:** each block below is labelled with the section it replaces. Copy the block, paste over
the matching section in the Google Doc, restyle headings. Anything inside **«»** is a decision or a
verification the researchers must make — do not paste those markers into the final paper.

---

# Part 0 — Three decisions needed before pasting

These three items are open questions in the comments that I cannot answer from the documents. Draft
text below assumes the first option; change it if your answer differs.

| # | Decision | Why it matters | Options |
|---|---|---|---|
| 1 | **Exact number of predefined gestures** | Comment [i]: "Clearly state the exact number of predefined gestures." | The gesture table in §3.2.1.7 shows **8** (activate, deactivate, and up/down for each of the three joints). Confirm against the actual gesture set. Draft says eight. |
| 2 | **Is the lamp's lighting function evaluated?** | Comment [i]: state whether brightness or only mechanical positioning is evaluated; whether the LED is part of functional testing. | (a) LED on/off + brightness implemented and reported only as a supporting function — **recommended, draft uses this**; (b) LED excluded entirely from the prototype scope; (c) LED lighting performance evaluated (adds illuminance measurement — not currently in the methodology). |
| 3 | **How is 0°–350° base rotation achieved?** | Comment [i]: "Explain whether the 0° to 350° base rotation is mechanically and electrically achievable." Comment [ac] adds that a 350° range "may require a special positional servo, multi-turn servo, geared mechanism, or another actuator arrangement." | (a) Continuous-rotation / multi-turn servo with position control; (b) standard servo + gear reduction to reach 350°; (c) keep the standard 180° servo and **reduce the stated range to 0°–180°**. Until the actuator is chosen, the range claim cannot be defended. |

---

# Part 1 — Chapter 1

## 1A. Standard terminology (apply everywhere, Chapters 1–3)

Comment [i] asks for one consistent term per joint. Standard set for the whole paper:

| Use this | Instead of | Where it appears now |
|---|---|---|
| **dual-mode** | hybrid | Title (done), Theoretical Framework, SOP, Objective 6, Scope bullet 1, §2.1.1.1, §3.1.5, §3.2.2.3 |
| **base rotation (yaw)** | Base Rotation (Yaw) | Scope, Delimitation, §3.2.1.7 table |
| **elbow pitch** | Elbow (Pitch); elbow or arm pitch; arm pitch | Scope, Delimitation, §2.1.1.2, §2.1.1.3, §2.3.x, §3.2.1.7 |
| **lamp-head pitch** | Lamp-Head Tilt (Pitch); lamp-head tilt; head pitch | Scope, Delimitation, §3.2.1.7 |

**Wording note.** "Dual-mode" describes two control methods available one at a time. Do not write
"hybrid control" anywhere; if a panel member asks, the answer is: the two modes are *combined in one
system* but never *operated simultaneously*, so the correct term is dual-mode, not hybrid.

**Replace in the Theoretical Framework (first sentence):**
> This study is anchored on three foundational theories that collectively explain the design and operating logic of the dual-mode gesture-based and mobile-controlled three-degree-of-freedom (3-DOF) smart lamp: General Systems Theory, Control Systems Theory, and Human-Computer Interaction (HCI) Theory. These theories provide the core scientific basis for the Input–Process–Output (IPO) structure of the system and its goal of optimized positional accuracy.

**Replace in §2.1.1.1 (last sentence of the closing paragraph):**
> This gap supports the objective of the present study, which is to design and develop a dual-mode gesture-based and mobile-controlled 3-DOF smart lamp and optimize its positional accuracy and repeatability through experimental calibration.

---

## 1B. Statement of the Problem — REPLACE the whole section

This adopts the adviser's revised version from comment [h], lightly edited for grammar and numbering.
It answers comments [c], [d], [g] and [h] in one move: it drops the redundant "which mode is more
accurate" question, removes the undefined "hybrid control system," and adds the functional measures
(reliability, response time) plus the pre/post-calibration comparison.

> ## Statement of the Problem
>
> This study aims to design and develop a dual-mode gesture-based and mobile-controlled
> three-degree-of-freedom (3-DOF) smart lamp and to evaluate its functional and positional
> performance before and after calibration. Specifically, this study seeks to answer the following
> questions:
>
> 1. What is the functional performance of the developed smart lamp in terms of:
>    1.1 gesture-command recognition reliability;
>    1.2 Bluetooth mobile-command execution reliability; and
>    1.3 command response time?
> 2. What are the positional error and repeatability of the base rotation (yaw), elbow pitch, and
>    lamp-head pitch joints before calibration?
> 3. What are the positional error and repeatability of the three joints after calibration?
> 4. Is there a significant difference between the pre-calibration and post-calibration positional
>    errors of the smart lamp?
> 5. Is there a significant difference in positional error between gesture-based and mobile-based
>    command input when equivalent target angles are used?

---

## 1C. Objectives — REPLACE the whole section

Old Objective 6 said "evaluate the performance of the developed hybrid system in terms of positional
accuracy and control reliability" — it is now split into the measurement work the adviser asked for.

> ## Objective of the Study
>
> ### General Objective
>
> This study aims to design and develop a dual-mode gesture-based and mobile-controlled
> three-degree-of-freedom (3-DOF) smart lamp and to evaluate and optimize its positional accuracy
> through open-loop control and experimental calibration.
>
> ### Specific Objectives
>
> 1. To design and construct a 3-DOF smart lamp mechanism capable of controlled movement along three
>    independent joints: base rotation (yaw), elbow pitch, and lamp-head pitch.
> 2. To develop a gesture-based control subsystem that converts a predefined set of hand gestures
>    into lamp movement commands.
> 3. To develop a Bluetooth-based mobile control subsystem that allows the user to issue angular
>    positioning commands from a smartphone application.
> 4. To integrate the gesture-based and mobile-based controls into a dual-mode system in which only
>    one mode is active at a time, with defined mode-selection and command-conflict handling.
> 5. To evaluate the functional performance of the developed system in terms of gesture-command
>    recognition reliability, Bluetooth mobile-command execution reliability, and command response
>    time.
> 6. To measure the positional error and repeatability of each joint before calibration by comparing
>    commanded target angles with externally measured actual angles.
> 7. To apply experimental calibration — zero-reference settings, servo limits, command-to-angle
>    mapping, and mechanical alignment — and re-measure positional error and repeatability under the
>    same target angles and procedure.
> 8. To compare the pre-calibration and post-calibration results, and the gesture-based and
>    mobile-based input conditions at equivalent target angles.

---

## 1D. Scope of the Study — REPLACE the list

Scope = what the study includes. (The current version mixes scope and delimitation; 1E fixes the
other half.)

> ### Scope of the Study
>
> - The study covers the design, development, integration, and experimental evaluation of a dual-mode
>   gesture-based and mobile-controlled 3-DOF smart lamp intended for indoor desk or workspace use.
> - The prototype consists of a mechanical lamp structure, three servo-actuated joints, an Arduino
>   Mega 2560 microcontroller, a Raspberry Pi Zero 2 W with camera for gesture recognition, an HC-05
>   Bluetooth module for mobile control, a power supply, and the control software.
> - The lamp provides three independently commanded rotational degrees of freedom with the following
>   ranges: base rotation (yaw) 0°–350°, elbow pitch 30°–150°, and lamp-head pitch 45°–135°. Base
>   rotation across the full range is provided by «DECISION 3: identify the actuator arrangement —
>   e.g. a continuous-rotation/multi-turn servo or a geared mechanism — and document it in
>   Section 3.1.4».
> - Two control methods are provided: a predefined set of eight hand gestures «DECISION 1: confirm
>   the number» recognized by the camera-based gesture subsystem, and manual commands issued through
>   a Bluetooth-enabled mobile application. Only one control mode is active at a time.
> - The prototype includes the lamp's basic lighting function (on/off and brightness control) through
>   the same controller. Lighting performance is not evaluated; «DECISION 2: confirm this treatment».
> - The lamp operates under open-loop control: movement commands are sent to the servo motors without
>   continuous position feedback, and no automatic position correction is applied during normal
>   operation.
> - Positional accuracy and repeatability are evaluated by comparing each commanded target angle with
>   the corresponding externally measured actual angle over repeated trials.
> - Functional performance is evaluated in terms of gesture-command recognition reliability, Bluetooth
>   mobile-command execution reliability, and command response time.
> - Positional accuracy is optimized through an experimental trial-and-error calibration process
>   covering servo calibration, zero-reference position, command-to-angle mapping, mechanical
>   alignment, joint tightness, and movement coordination.
> - The initial and optimized configurations of the prototype are compared to determine whether
>   calibration reduces positional error and improves repeatability.
> - Experimental testing is conducted in a controlled indoor desk or workspace environment, with all
>   measurements taken using the instruments specified in the methodology.

## 1E. Delimitation of the Study — REPLACE the list

Delimitation = the boundaries the researchers deliberately set. Each bullet is a boundary, not a
description.

> ### Delimitation of the Study
>
> - The study is limited to a functional 3-DOF smart lamp prototype for indoor desk or workspace use.
>   Commercial manufacturing, mass production, industrial certification, and heavy-load applications
>   are excluded.
> - Joint movement is limited to the stated ranges: base rotation (yaw) 0°–350°, elbow pitch
>   30°–150°, and lamp-head pitch 45°–135°. No additional degrees of freedom, such as telescoping or
>   translation, are included.
> - The gesture-based control system is limited to the predefined gesture set. Sign-language
>   recognition, full-body gestures, and autonomous user tracking are not included.
> - The mobile-control system is limited to Bluetooth communication. Wi-Fi, internet-based control,
>   cellular communication, and cloud control are excluded.
> - Only one control mode may be active at a time; simultaneous commands from both modes are not
>   permitted.
> - The study is limited to open-loop control. Continuous closed-loop feedback and automatic position
>   correction are not implemented; external angle measurement is used only for evaluation and
>   offline calibration.
> - Positional accuracy optimization is limited to experimental trial-and-error calibration.
>   Machine-learning-based optimization of joint positions is not included.
> - Actual joint angles are measured only with the external angular measuring instruments selected
>   for the experimental setup, such as a protractor, calibrated angular scale, or digital angle
>   measuring device.
> - The lighting function is limited to basic on/off and brightness control. Lighting performance
>   measures such as illuminance, color quality, and eye-safety compliance are outside the scope of
>   the study. «DECISION 2»
> - The findings are limited to the specific hardware, mechanical structure, materials, and software
>   configuration of the developed prototype.
> - Testing is limited to a controlled indoor environment; extreme outdoor and environmental
>   conditions are not covered.
> - The study is limited to positional accuracy, repeatability, command execution, and functional
>   performance of the two control modes. Long-term durability, reliability under continuous use, and
>   load-capacity testing are excluded.
> - Because the system is evaluated with camera-based gesture input, the study is limited to
>   situations in which the user's hand is visible to the camera and the workspace lighting and
>   background conditions are within the range established during preliminary testing.

---

## 1F. Definition of Terms — REPLACE the whole section

Comment [l] asked for conceptual **and** operational definitions. Each entry below gives both:
conceptual first (general meaning, as used in the literature), then operational (how it is used and
measured in *this* study).

> ## Definition of Terms
>
> **3-DOF (Three Degrees of Freedom).** *Conceptual:* the number of independent coordinates required
> to describe the configuration of a mechanical system; a 3-DOF mechanism therefore has three
> independently controllable motions. *Operational:* in this study, the three independently commanded
> rotational joints of the lamp — base rotation (yaw), elbow pitch, and lamp-head pitch — whose
> combined angular positions determine the position and orientation of the lamp head.
>
> **Absolute Positional Error.** *Conceptual:* the magnitude of the difference between a commanded
> position and the position actually reached, expressed without sign. *Operational:* computed for
> each joint as |Target Angle − Actual Angle| in degrees, where the actual angle is measured
> externally after the joint has settled.
>
> **Arduino Mega 2560.** *Conceptual:* a microcontroller development board based on the ATmega2560,
> providing digital and analog input/output pins and multiple hardware serial ports. *Operational:*
> the main controller of the prototype. It receives commands from the Raspberry Pi Zero 2 W in
> gesture mode or from the HC-05 module in mobile mode, and drives the three servo motors and the
> lamp's lighting circuit.
>
> **Bluetooth.** *Conceptual:* a short-range wireless communication standard used to exchange data
> between electronic devices without a physical connection. *Operational:* the communication medium
> of the mobile control mode. Commands issued in the mobile application are transmitted to the HC-05
> module and forwarded to the Arduino Mega 2560 through UART serial communication.
>
> **Calibration.** *Conceptual:* the process of determining and applying corrections so that a
> commanded value corresponds more closely to the physical value actually produced. *Operational:*
> the experimental adjustment of zero-reference positions, servo limits, and command-to-angle mapping
> performed by comparing commanded target angles with externally measured actual angles, carried out
> before and after the adjustments to determine whether positional error is reduced.
>
> **Command Reliability.** *Conceptual:* the degree to which a control input is correctly interpreted
> and executed by the system. *Operational:* reported as a success rate — the number of correct
> recognitions or executions divided by the total number of attempts, multiplied by 100. For gesture
> control, correct recognitions, incorrect recognitions, and failed detections are recorded
> separately; for mobile control, the successful execution of transmitted commands is verified.
>
> **Dual-Mode Control.** *Conceptual:* a control scheme in which two alternative input methods are
> available to the same system but are operated one at a time. *Operational:* the availability of
> gesture-based and Bluetooth mobile control in one lamp, with only one mode active at any moment;
> mode selection, mode deactivation, and the handling of invalid or repeated commands are defined in
> Chapter 3. In this study, "dual-mode" is used instead of "hybrid control," because the two modes are
> never operated simultaneously.
>
> **Gesture Recognition.** *Conceptual:* the interpretation, by a computing system, of human hand
> configurations captured by a camera as discrete commands. *Operational:* the recognition of a
> predefined set of hand gestures through the MediaPipe hand-landmark model, with each recognized
> gesture mapped to a specific lamp command; recognition reliability is measured as defined under
> Command Reliability.
>
> **HC-05.** *Conceptual:* a Bluetooth Serial Port Profile (SPP) module used to provide wireless
> serial communication to microcontroller-based systems. *Operational:* the module that receives
> commands from the Bluetooth-enabled mobile application and forwards them to the Arduino Mega 2560
> through UART.
>
> **Open-Loop Control.** *Conceptual:* a control approach in which the control action is determined by
> a predefined command without using the measured output as feedback for automatic correction.
> *Operational:* the normal operating mode of the lamp. Servo commands are executed without
> continuous position feedback, and actual joint angles are measured externally only for evaluation
> and offline calibration, not for real-time correction.
>
> **Positional Accuracy.** *Conceptual:* how closely a mechanical or robotic system reaches its
> intended or commanded position. *Operational:* evaluated through the positional error of each joint
> in degrees, as defined above. Where a single index is required for comparison, positional accuracy
> may be expressed as a percentage, (1 − |T − A| / R) × 100, where T is the target angle, A is the
> actual angle, and R is the defined operating range of the joint; because percentage values are
> sensitive to the choice of R and are not meaningful near 0°, joint error is reported primarily in
> degrees.
>
> **Repeatability.** *Conceptual:* the closeness of agreement among repeated measurements of the same
> quantity under the same conditions. *Operational:* evaluated from repeated trials at the same target
> angle and starting condition, reported through the standard deviation and the maximum deviation from
> the trial mean; the number of trials per condition is justified and applied consistently in
> Chapter 3.
>
> **Response Time.** *Conceptual:* the elapsed time between the issuance of a command and the system's
> response to it. *Operational:* measured from the presentation of the gesture or the transmission of
> the mobile command to the start of servo movement «recommended: the start of movement, which
> isolates recognition and transmission latency from servo travel time, which varies with the
> commanded angular distance. Select one endpoint and apply it consistently — comment [am]».
>
> **Servo Motor.** *Conceptual:* a rotary actuator that uses internal position feedback to hold a
> commanded angular position. *Operational:* the three actuators that drive the base, elbow, and
> lamp-head joints of the lamp. The model, operating voltage, torque rating, and assigned joint of
> each servo are documented in Chapter 3 «comment [ac]».
>
> **Target Angle.** *Conceptual:* the angular position specified for a joint by the control system.
> *Operational:* the angle, in degrees, that is sent to a servo by either the gesture-based or the
> mobile command path during testing, and against which the actual angle is compared.
>
> **Actual Angle.** *Conceptual:* the angular position physically reached by a joint. *Operational:*
> the angle measured externally with the selected measuring instrument after the joint has settled;
> this value is not returned to the controller during normal operation.
>
> **Yaw.** *Conceptual:* rotation about a vertical axis. *Operational:* the type of rotation performed
> by the base joint of the lamp, commanded within its defined range «DECISION 3».
>
> **Pitch.** *Conceptual:* rotation about a horizontal axis that raises or lowers a link of a
> mechanism. *Operational:* the type of rotation performed by the elbow joint and the lamp-head
> joint, commanded within 30°–150° and 45°–135° respectively.
>
> **Hybrid Control.** *Not used in this study.* The term was replaced by "dual-mode control" because
> the two control methods are never operated simultaneously. If the panel requires the term to be
> retained, define it as: *the combined availability of gesture-based and mobile control within one
> system, operated one mode at a time* — the same meaning as dual-mode control.

---

## 1G. Chapter 1 — remaining line fixes

| Location | Problem | Fix |
|---|---|---|
| Significance, "Users" | Acceptable, but confirm it still reads correctly after the SOP change | No text change needed |
| SOP, all | The old Q2/Q3 overlap and the undefined "hybrid control system" — fixed by 1B | Replace section |
| General Objective | Still said "hybrid" in the old SOP paragraph | Covered by 1C |
| §1 Background | Clean; matches [e] and [f] | No change |

---

# Part 2 — Chapter 2

## 2A. Chapter 2 terminology and framing fixes

| Where | Now | Change to |
|---|---|---|
| §2.1.1.1, last sentence | "…hybrid gesture-based and mobile-controlled 3-DOF smart lamp…" | "…dual-mode gesture-based and mobile-controlled 3-DOF smart lamp…" |
| §2.1.2, last sentence | "…gesture-recognition reliability will remain a secondary performance measure because the main evaluation focuses on the positional accuracy and repeatability…" | See replacement below — comment [d] makes reliability a *functional* performance measure, not a mere afterthought |
| §2.1.1.2 / §2.1.1.3 | "elbow or arm pitch" | "elbow pitch" |

**Replace the last sentence of §2.1.2:**
> In the present study, the same general sequence will be followed: camera input, visual processing, predefined gesture identification, command generation, and servo-actuated lamp movement. Vision-based hand-gesture recognition will serve as the primary control input, and gesture-recognition reliability will be evaluated as a functional performance measure alongside the positional accuracy and repeatability of the 3-DOF lamp mechanism.

## 2B. New paragraph for §2.1.5 — distinguishing the error measures

Comment [n] asks the paper to distinguish positional accuracy, recognition accuracy, tracking error,
trajectory error, and localization error, and warns against comparing percentages, degrees, and
millimeters as equivalent. Paste this at the end of §2.1.5:

> The reviewed literature reports several different measures that should not be treated as
> interchangeable. **Positional (angular) error** is the difference between a commanded joint angle
> and the angle actually reached, expressed in degrees, and is the primary measure of the present
> study. **Recognition accuracy** describes the proportion of gestures or objects that a vision system
> classifies correctly; it is a property of the recognition subsystem rather than of the mechanism,
> and is reported in the present study as a separate functional measure. **Tracking or trajectory
> error** describes the deviation of a moving system's path from a commanded path over time and is
> expressed in distance units, as in the mobile-controlled robot study of Dimalanta et al. (2023).
> **Localization error** describes the difference between the estimated position of a target in a
> coordinate frame and its true position, as reported in millimeters by Sun and Liu (2023). Because
> these measures arise from different subsystems and are expressed in different units, their values
> are not directly comparable; accordingly, this study reports angular error in degrees for the
> positioning evaluation and command reliability and response time as separate functional measures.

## 2C. §2.2.6 – §2.2.10 — REPLACE all five subsections

These follow the standard structure the adviser asked for in comment [q]: author and year → purpose →
system or methodology → measured results → relevance to the present study → difference or gap. The
informal 2.0 versions (and the four sentences quoted in comment [p]) are removed; the formal 1.0
content and its data are retained. Also rename the headings so each names its source.

> ### 2.2.6 Accuracy Test of an Open-Loop Control System for Arduino-Based Robotic Arms with a PLA+ 3D-Printed Body for Repetitive Tasks (Suryadarma et al., 2025)
>
> Suryadarma et al. (2025) developed and evaluated an Arduino-based robotic arm with an open-loop
> control system in order to determine its accuracy and repeatability in performing repetitive tasks.
> The arm was constructed with a PLA+ 3D-printed structure, selected for its favorable mechanical
> properties, ease of fabrication, and suitability for producing cost-effective robotic components.
> The system used an Arduino Mega as its main controller and stepper motors to drive a mechanism with
> three degrees of freedom together with a translational rail.
>
> Because the system operated under open-loop control, it ran without continuous positional feedback.
> This reduced the hardware requirements and complexity of the system, but the absence of real-time
> feedback limited its ability to detect and correct positional errors during operation. To evaluate
> accuracy and repeatability, the researchers conducted 30 repetitive trials in which the arm moved
> between predefined positions over a travel distance of 500 mm, measuring the difference between the
> programmed target position and the actual position reached by the end effector.
>
> The positional bias generally ranged from approximately 0 to 1.2 mm, with a mean bias of
> approximately 0.593 mm. The results also showed no significant trends or oscillations in the
> recorded positional errors across the trials, indicating that an open-loop Arduino-based arm can
> achieve reasonable accuracy and repeatability when performing predefined repetitive movements under
> controlled conditions. The researchers emphasized, however, that further improvements are necessary
> to enhance precision and consistency, and that the absence of feedback limits the system's ability
> to respond to external disturbances or changing operating conditions.
>
> This study is relevant to the present work because it demonstrates that an open-loop, multi-DOF
> mechanism can be evaluated by comparing programmed target positions with measured actual positions
> over repeated trials. Two differences limit direct comparison. First, the reported error is linear
> (millimeters of end-effector travel), whereas the present study measures angular error in degrees
> at each joint. Second, the mechanism is driven by stepper motors rather than position-controlled
> servo motors, so its error behavior does not transfer directly to the servo-actuated joints of the
> smart lamp.
>
> ### 2.2.7 Gesture-Based Robotic Control (Wen et al., 2022)
>
> Wen et al. (2022) developed a gesture-controlled robotic arm capable of replicating movements
> performed by a human operator. The system used accelerometers, an MPU6050 motion sensor, two
> Arduino Mega microcontrollers, servo motors, and NRF24L01 wireless communication modules.
>
> In this system, the motion sensors detected the movement of the operator's arm and transmitted the
> corresponding data to the robotic system. These signals were used to control the joints of the arm,
> allowing it to reproduce the operator's gestures without direct physical contact. The study
> therefore demonstrates that gesture-based input can be converted into coordinated joint movement in
> an electromechanical system.
>
> The study is relevant to the present research because both systems use gesture-based interaction to
> control an articulated device. The difference lies in the sensing method: Wen et al. (2022) relied
> on wearable motion sensors, whereas the proposed smart lamp uses camera-based gesture recognition,
> which requires no device to be worn by the user. The studies also differ in their evaluation
> objective: Wen et al. evaluated movement replication, while the present study evaluates command
> reliability and the positional accuracy of three servo-actuated joints.
>
> ### 2.2.8 Mobile-Controlled Servo Positioning (Alsayaydeh et al., 2025)
>
> Alsayaydeh et al. (2025) developed a five-degree-of-freedom robotic arm controlled through a mobile
> application. The system used an Arduino Mega 2560, MG996R servo motors, and an HC-05 Bluetooth
> module for wireless communication. The mobile application was created with MIT App Inventor and
> provided buttons and sliders for controlling individual joints, allowing users to adjust each
> servo motor through a wireless interface.
>
> The researchers evaluated the positional accuracy of the arm by comparing commanded angles with
> actual measured angles. In their tests, a target shoulder angle of 150° produced an actual position
> of 143°, while a target elbow angle of 180° produced 168°. The system achieved an overall accuracy
> of approximately 94.67%, and the observed differences were attributed to servo limitations,
> mechanical construction, and system calibration.
>
> This study is relevant to the proposed smart lamp because both systems use the same control chain —
> a mobile application, Bluetooth communication, a microcontroller, and servo motors — and both
> evaluate performance by comparing commanded and measured joint angles. The two systems differ in
> configuration and scope: Alsayaydeh et al. (2025) controlled a five-degree-of-freedom arm with a
> single control interface, whereas the present study uses three joints, provides two selectable
> control modes, and compares positional error before and after calibration.
>
> ### 2.2.9 Open-Loop Multi-DOF Positioning (RoboVR, 2025) «complete citation needed»
>
> A 2025 study developed RoboVR, a low-cost four-degree-of-freedom robotic arm controlled through an
> Arduino-based open-loop system. Joint-angle commands were converted into pulse-width modulation
> (PWM) signals to drive the servo motors. Because the system lacked positional feedback, the
> researchers compared the commanded joint angles with the actual servo positions during testing.
>
> The results showed varying positional errors across the joints. Average errors of approximately
> −1.60° and 1.8° were observed during basic movements, while an individual elbow movement produced
> an average error of about 1.43°. Greater deviations were reported at the shoulder joint,
> demonstrating that open-loop control can produce differences between intended and actual positions.
>
> This study is relevant to the proposed 3-DOF smart lamp because it also employs an open-loop
> positioning approach and evaluates it by comparing commanded with measured joint angles in degrees —
> the same unit and logic used in the present study. The difference is one of application and
> configuration: RoboVR is a four-degree-of-freedom arm evaluated through freedom-of-movement tests,
> while the present study evaluates three servo-actuated joints of a lamp, reports the results before
> and after calibration, and relates them to two alternative command sources.
>
> «Comment [n] requires complete citation details where the author names are missing. The RoboVR study
> is cited in the draft without authors. Retrieve the full reference (authors, title, source) before
> final submission — do not guess.»
>
> ### 2.2.10 Servo Error Compensation for a Robotic-Arm Manipulator (Kiswanto et al., 2021)
>
> Kiswanto et al. (2021) developed a control system for a robotic-arm manipulator using an Arduino
> Mega 2560 to control servo and stepper motors, with computed joint values sent to the actuators
> through commands generated in the Arduino IDE. The system was developed in the context of
> micromilling tool wear monitoring.
>
> During testing, the researchers found positioning inaccuracies in three servo motors, with
> differences of about 16.471%, 1.463%, and 0.588%. After error compensation was applied, the
> reported errors decreased to 0.003%, 0.143%, and −0.382%. The researchers also examined the
> consistency of the mechanism and found that the control system placed the end effector closer to
> the target once the adjustments had been made.
>
> This study directly supports the calibration approach of the present work. In both cases,
> differences between commanded positions and externally determined positions are identified and used
> as the basis for correcting the commands, while the system remains open-loop. The difference is
> scope and unit of analysis: Kiswanto et al. (2021) reported error as a percentage for a manipulator
> used in a machining-monitoring application, whereas the present study reports angular error in
> degrees for the three servo-actuated joints of a lamp and evaluates repeatability as well as error.

**Note on 2.2.10's original number.** If the percentage figures in Kiswanto et al. (2021) are
reported per servo without a stated reference range, do not convert or combine them with degree-based
results elsewhere in the chapter — this is exactly the comparison comment [n] warns against.

## 2D. Formality fixes for §2.2.1 – §2.2.5

These five subsections were not flagged for a rewrite (comment [o] targets 2.2.6–2.2.10), but they
carry informal phrasing and comment [n] asks for a uniform academic tone. Sentence-level replacements:

| § | Now | Change to |
|---|---|---|
| 2.2.1 | "Flipping on a light switch may be considered a common act among most people, but there are some who find it extremely difficult to perform such an act." | "Operating a light switch is a routine action for most users, but it can be difficult for some individuals." |
| 2.2.1 | "The device came out excellent in both sensitivity ratings." | "The device performed well under both sensitivity ratings." |
| 2.2.1 | "Of all the papers in this subsection, theirs is the one that operates most like the proposed lamp, since the entire purpose of the device is that hand movements alone switch the light, with no switch in the way." | "Among the studies reviewed in this subsection, this system is the most closely related to the proposed lamp, because it is intended to switch the light through hand movement alone, without a physical switch." |
| 2.2.1 | "The common ground ends there, though." | "The similarity ends there, however." |
| 2.2.2 | "Not every letter came easily: Q, J, and Z were difficult…" | "Recognition performance varied by letter: Q, J, and Z were difficult…" |
| 2.2.2 | "For the proposed lamp, the value of the paper lies mainly in the hardware lesson…" | "For the proposed lamp, the main contribution of this study is the hardware evidence that…" |
| 2.2.2 | "The resemblance thins out at the output stage." | "The similarity is limited at the output stage, however." |
| 2.2.3 | "It is easy to assume that the controller has nothing to do with how precisely a machine moves, but Dimalanta et al. (2023) of the University of Santo Tomas showed otherwise." | "Dimalanta et al. (2023) of the University of Santo Tomas demonstrated that the control interface can affect how precisely a machine follows a commanded path." |
| 2.2.3 | "Two lessons carry over to the smart lamp." | "Two findings are relevant to the present study." |
| 2.2.3 | "The objects under control, of course, could hardly be more different…" | "The mechanisms differ substantially, however…" |
| 2.2.4 | "What this means for the present work is mostly reassurance…" | "The main implication for the present work is that…" |
| 2.2.5 | "Robots rarely arrive exactly where their controllers intend them to…" | "Controlled mechanisms do not always reach the position intended by their controllers…" |
| 2.2.5 | "Just as interesting was the error that would not go away." | "Notably, one component of the error could not be corrected." |

## 2E. Validation tables — restore consistency

In 2.0 the Validation column of the Root Cause table is blanked for rows 1–4 and 7 (only rows 5 and 6
still read VALID/INVALID), and the entire Solution table is blank, while the prose in §2.3.2.1–2.3.2.7
still declares each cause VALID. Pick one treatment and apply it everywhere. Recommended:

**Restore all cells** to the literature-based judgments (Root Cause rows 1–5 = VALID, row 6 =
INVALID, row 7 = VALID; Solution rows 1–7 = VALID), and add this note immediately after each table:

> Note: "VALID" in this table means that the candidate cause or solution is supported by the reviewed
> literature and technical evidence. It does not mean that the cause has been confirmed for the
> developed prototype. As stated in Section 2.3.1, the actual contribution of each candidate cause
> will be established only through testing of the prototype.

This satisfies comment [v] ("root causes are not fully confirmed until evaluated using prototype
data") without leaving the tables in a half-edited state. Comment [y] explicitly praised these tables
for their traceability — an empty column loses that value.

## 2F. Fishbone diagram — content spec for regeneration

Comment [v] asks for the diagram to be regenerated legibly and without crossed-out text. The figure
itself cannot be edited from the text export, so the specification below is what the redrawn diagram
should contain. «Confirm the placement of each cause on its bone before redrawing.»

**Head (the effect):** positional inaccuracy and control performance of the 3-DOF smart lamp.

| Bone | Candidate causes to place on it |
|---|---|
| **User** | Suboptimal hand-gesture execution and recognition (Root Cause 1) |
| **Method** | Gesture-to-command mapping; mode selection procedure; calibration procedure |
| **Machine** | Servo and control parameters: servo characteristics, zero-reference settings, command-to-angle mapping, servo limits (Root Cause 3) |
| **Material** | Insufficient structural stiffness and joint support: joint looseness, sag, deflection, servo mounting (Root Cause 7) |
| **Measurement** | Angular measurement method and instrument alignment; prototype placement and setup geometry (Root Cause 6 — retained here as an experimental-control factor, not as a confirmed cause) |
| **Environment** | Hand-to-camera distance (Root Cause 2); camera view obstruction/occlusion (Root Cause 4); workspace lighting and visual conditions (Root Cause 5) |

Two labeling requirements: the caption should read **"Figure 2.X Candidate causes of positional
inaccuracy and control variation (Ishikawa diagram)"** — the word *candidate* matters, per comment
[v] — and the seven numbered root causes should keep the same numbers used in §2.3.2 so the figure
and the tables stay traceable.

## 2G. Chapter 2 line-level corrections

| Location | Now | Change to |
|---|---|---|
| §2.1.5 | "Sutisna et al. (2022)  Found quantifiable errors in an arduino-based robotic arm that was managed by a mobile application, according to their research, servo commands may…" | "Sutisna et al. (2022) found quantifiable errors in an Arduino-based robotic arm controlled by a mobile application; according to their study, servo commands may…" |
| §2.1.5 | "Kiswanto et al. (2021) Showed" | "Kiswanto et al. (2021) showed" |
| §2.2.2 | "The selected task involved Filipino Sign Language (FSL) In their pipeline," | "The selected task involved Filipino Sign Language (FSL). In their pipeline," |
| §2.2.3 | "…used using the joystick interface.." / any doubled period | single period |
| §2.3.2, row 6 | "…demonstrates an independent effect.." | "…demonstrates an independent effect." |
| §2.2.6 – 2.2.9 | informal constructions, doubled periods | replaced by 2C |
| §2.3.x headings | "2.3.1.1 Fishbone Diagram of the Study" and body refer to "Figure 2.X" and "Figure 2.5" for the same diagram | use one figure number consistently |

---

# Part 3 — After Chapter 1 and 2 are done

Not part of this pack, listed so nothing is lost:

| Item | Comment | Status |
|---|---|---|
| Chapter 3 completion: weight, actuators, voltage, camera selection, functionality testing, calibration procedure, data processing, target error, phone-controller testing | [z] | Not started |
| Chapter 3 required additions: research design, architecture, block and wiring diagrams, BOM, sampling/trial plan, testing procedure, instruments, formulas, statistical treatment, safety, acceptance criteria, ethics/privacy | [aa] | Not started |
| Per-component materials, bearings, cable routing, mechanical stops | [ab] | Not started |
| Servo documentation incl. torque calculations and the 350° arrangement | [ac] | Not started — blocked on Decision 3 |
| Pi↔Arduino protocol, command format, mode logic, conflict prevention, voltage, grounding, e-stop, startup, invalid commands, separate servo supply, Bluetooth takeover | [ad] | Not started |
| ML contradiction: pretrained MediaPipe model is still machine learning | [ae], [af] | Not started — the recommended wording in [af] is ready to paste into §3.2.1.2 |
| MediaPipe details: model, version, license, threshold, frame rate, debounce, unknown gestures, hand handling, trial count, definitions of correct/incorrect/failed | [ag] | Not started |
| Camera-data privacy: consent, storage, retention, deletion | [ah] | Not started |
| Measurement formulas and statistics: MAE, signed error, accuracy formula, repeatability measures, recognition success rate, response-time definition, statistical treatment | [ai]–[an] | Not started — the Definition of Terms in 1F already carries the conceptual versions |
| Figures: IPO diagram, gesture table illustrations, SolidWorks views — verify quality and numbering | [c], [aa] | Not verifiable from text |

---

*Working document, 2026-10-02. Prepared against the 1.0 and 2.0 captures in this archive; if the Google
Docs change, re-check before pasting.*
