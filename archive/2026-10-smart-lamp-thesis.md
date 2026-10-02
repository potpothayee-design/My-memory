# Smart lamp — capstone working doc (CPE Practice & Design 1, 2026-10)

**Cold layer.** Fetched only when the topic is the smart lamp / capstone thesis. Not loaded by default.

**Full text capture** of the project's Google Doc, taken **2026-10-02**, including the adviser's
inline review comments. This is a snapshot, not an edited copy — wording below is verbatim from the
source, typos and all.

| | |
|---|---|
| **Source doc** | <https://docs.google.com/document/d/1B9gGsveGdoZo4Q98j_XE9InB3YJbrrLxWkkwlZh9tjI/edit> |
| **File ID** | `1B9gGsveGdoZo4Q98j_XE9InB3YJbrrLxWkkwlZh9tjI` |
| **Captured** | 2026-10-02 |
| **Method** | Google Docs HTML export, read as text (bash `curl` cannot reach the network from this sandbox — the assistant's fetch tool can) |
| **Not captured** | **All images/figures.** The text export left ~19 image placeholders. Figures, the fishbone diagram, the gesture illustrations, and the SolidWorks shots have to come from the source doc. |
| **Status** | Draft. Chapter 3 is incomplete — many subheadings have no body text yet. |

Reading aids used below:
- `[figure — in source doc only]` marks where an image sits in the original.
- *(empty in source)* marks a heading with no body text yet.
- `[a]` … `[an]` are the adviser/editor comment anchors; the full comment text is in the last section.

**Related in this repo:** the `final_sure_part_1*.aia` / BLE robot-arm work is the same lamp
hardware — same joints and limits (base 0–350°, elbow 30–150°, head 45–135°), same `H/E/B/P/TW/TN/TC/M1/M0`
command protocol. See `archive/2026-10-robot-arm.md`.

---

## Cover page

**IETI COLLEGES OF SCIENCES & TECHNOLOGY, INC** [a][b][c][d]

SAN PEDRO CAMPUS

CITY OF SAN PEDRO LAGUNA

COLLEGE OF ENGINEERING

COMPUTER ENGINEERING DEPARTMENT

A.Y. 2026 – 2027

### Design and Development of a Hybrid Gesture-Based and Mobile-Controlled Three-Degree-of-Freedom Smart Lamp through Positional Accuracy Optimization

In partial fulfillment of the requirements for the course

**CPE Practice & Design 1**

**Members:**

- Camartin, Zydrick Hayee Y.
- Clemente, Alvin A., Jr.
- Furio, Rodel C., Jr
- Hamto, John
- Olleta, Christian Aldrin B.

IETI CpE 4

**Presented to:**

Engr. Airelyssa E. Peñalosa, ECT, DE, CLSSYB, CIS

---

## Table of Contents

- Abstract
- Chapter 1 — Introduction
- Chapter 2 — Review of Related Literature
- Chapter 3 — Methodology
- Chapter 4 — Data and Findings
- Chapter 5 — Summary / Conclusion / Recommendation
- Appendix
- Bibliography

---

## Abstract

*(empty in source)*

---

# Chapter 1 — INTRODUCTION [e][f]

## Background

Advances in embedded systems, computer vision, microcontrollers, and wireless communication have made electronic and electromechanical devices easier to control in flexible ways. Instead of relying only on traditional buttons and switches, some systems can now respond to hand gestures and commands from mobile applications. Gesture-based control has also been applied to robotic and motorized mechanisms, where human movements are interpreted as commands that produce physical motion (Yu et al., 2024; Abuan, 2023). This supports vision-based gesture control for a motorized smart lamp.

The proposed three-degree-of-freedom (3-DOF) smart lamp has three controlled movements: base or yaw rotation, elbow or arm pitch, and lamp-head pitch. The combined angular positions of these joints determine the position and orientation of the lamp head. Similar articulated mechanisms show that coordinated movement across connected joints can position a physical system (Iadanza et al., 2023). Servo motors will move each joint according to the angle commanded by the control system.

The lamp will use two selectable control methods. Vision-based hand-gesture recognition will serve as the primary control method, while a Bluetooth-enabled mobile application will serve as the secondary control method. These modes will operate independently, so only one method will send movement commands at a time. In this study, hybrid refers to combining two available control methods in one system rather than operating them simultaneously. Princewill et al. (2023) also demonstrated smartphone control of a multi-DOF mechanism.

Even when the correct command is sent, the actual joint angle may not always match the intended position. The smart lamp will therefore use an open-loop control approach, where measured joint positions are not continuously returned to the controller for automatic correction during normal operation. Differences between commanded and actual positions may be influenced by servo characteristics, mechanical alignment, structural loading, zero-reference settings, angular mapping, power conditions, and calibration. These factors will only be considered causes if supported by experimental results. Related work also shows the importance of comparing intended and actual movement during position checking (Munsayac et al., 2024).

The prototype will be evaluated by comparing the commanded angle of each joint with its actual measured angle. Absolute positional error will be determined using Absolute Positional Error = |Target Angle − Actual Angle|. Repeated trials will evaluate how consistently the lamp reaches the same target position. Positional accuracy and repeatability will serve as the primary performance measures, while gesture-recognition reliability, Bluetooth command reliability, and response time will serve as secondary measures. Trial-and-error calibration will be performed to determine whether positional error can be reduced and consistency improved.

Previous studies have examined gesture-controlled mechanisms, Bluetooth-based control, multi-DOF servo systems, and positional performance in robotic and automation applications. However, limited work was identified within the reviewed literature that combines vision-based hand-gesture control, Bluetooth-based secondary control, 3-DOF servo-actuated lamp movement, and experimental positional-accuracy optimization in one physical smart-lighting prototype. Therefore, this study focuses on integrating these components into a functional 3-DOF smart lamp and evaluating its positioning performance through measurement, repeated testing, and calibration.

## Theoretical Framework

This study is anchored on three foundational theories that collectively explain the design and operating logic of the Hybrid Gesture-Based and Mobile-Controlled Three-Degree-of-Freedom (3-DOF) Smart Lamp: General Systems Theory, Control Systems Theory, and Human-Computer Interaction (HCI) Theory. These theories provide the core scientific basis for the Input–Process–Output (IPO) structure of the system and its goal of optimized positional accuracy.

[figure — in source doc only]

**Figure 1. IPO Diagram**

### General Systems Theory

The general model of the current study is based on the general systems theory put forward by Ludwig von Bertalanffy (1968). The idea behind the theory is that any process can be viewed as an interaction of interdependent elements that include inputs, processes of transformation, and outputs aimed at achieving one common goal. Thus, the Input–Process–Output (IPO) model can be considered appropriate for structuring the present research since it allows viewing the smart lamp as an integrated closed system aimed at the goal of optimal positioning accuracy.

### Control Systems Theory (Open-Loop Control)

Open-loop control theory describes a system in which the control action is determined by a predefined command without using the actual system output as feedback for automatic correction (Ogata, 2010). In an open-loop positioning system, performance depends on factors such as actuator characteristics, mechanical configuration, and proper calibration because positional errors are not automatically corrected during operation.

In this study, open-loop control theory underlies the positioning mechanism of the three-degree-of-freedom smart lamp. Each joint is driven by a servo motor according to a commanded angle generated from either a gesture or mobile command. The main control system does not receive external position feedback to verify or automatically correct the actual joint position during operation. Instead, positional accuracy is improved through calibration of the command-to-position relationship and evaluated experimentally by externally measuring the actual position and comparing it with the commanded position.

### Human-Computer Interaction (HCI) Theory

The input stage of the framework, particularly the use of gesture sensors and a mobile application as command sources, is grounded on Human-Computer Interaction (HCI) theory and Donald Norman's (1988) theory of interaction design. Norman's theory emphasizes designing systems whose controls map naturally and intuitively to user intent, reducing the cognitive effort required to operate a device. This principle justifies the choice of gesture recognition and mobile-based control as natural, low-friction input modalities for directing the movement of the 3-DOF lamp mechanism.

## Statement of the Problem [g][h]

This study aims to design and develop a hybrid gesture-based and mobile-controlled three-degree-of-freedom (3-DOF) smart lamp through positional accuracy optimization. Specifically, it seeks to determine the positional accuracy and controller performance of the smart lamp under gesture-based, mobile-based, and hybrid control modes.

Specifically, this study seeks to answer the following questions:

1. What is the positional accuracy of the 3-DOF smart lamp when controlled through:
   1.1. gesture-based input; and
   1.2. mobile-based input;
2. Is there a significant difference in the positional accuracy of the 3-DOF smart lamp between gesture-based control and mobile-based control?
3. Which control mode—gesture-based, mobile-based—provides the highest positional accuracy in positioning the 3-DOF smart lamp?
4. How effective is the proposed hybrid control system in optimizing the positional accuracy of the 3-DOF smart lamp based on the measured deviation between the target and actual positions?

## Objective of the Study

### General Objective

This study aims to design and develop a dual-mode gesture-based and mobile-controlled three-degree-of-freedom (3-DOF) smart lamp and optimize its positional accuracy through open-loop control and experimental calibration methods.

### Specific Objective

1. To design and construct a 3-DOF smart lamp mechanism capable of controlled movement along three independent joints or axes.
2. To develop a gesture-based control subsystem that allows users to adjust the lamp's position through predefined hand gestures.
3. To develop a mobile application-based control subsystem that allows users to manually adjust the lamp's position.
4. To integrate the gesture-based and mobile-based controls into a dual-mode control system in which only one control mode can be selected and operated at a time.
5. To implement an open-loop control and calibration method that optimizes the positional accuracy of each degree of freedom through calibrated servo angle commands.
6. To evaluate the performance of the developed hybrid system in terms of positional accuracy and control reliability.

## Scope and Delimitation [i]

### Scope of the Study

- The study covers the design, development, integration, and experimental evaluation of a hybrid gesture-based and mobile-controlled three-degree-of-freedom smart lamp.
- The prototype consists of a mechanical lamp structure, servo motors, microcontroller, camera-based gesture recognition system, Bluetooth-enabled mobile control interface, power supply, and required control software.
- The smart lamp provides three controllable degrees of freedom: Base Rotation (Yaw) 0°–350°, Elbow (Pitch): 30°–150°, Lamp-Head Tilt (Pitch): 45°–135°.
- The system uses two control methods: predefined hand gestures through camera-based gesture recognition and mobile control through Bluetooth communication.
- The gesture-based and Bluetooth mobile-control modes will operate independently, and only one control mode will be active at a time.
- The smart lamp uses an open-loop control system, where movement commands are sent to the servo motors without continuous external position feedback.
- The study evaluates the positional accuracy and repeatability of the three joints by comparing the commanded target angle with the actual measured angle through repeated experimental trials.
- Positional accuracy will be improved through an experimental trial-and-error calibration process, including adjustments to servo calibration, zero-reference position, angle mapping, mechanical alignment, joint tightness, and movement coordination.
- The initial and optimized configurations of the prototype will be compared to determine whether the calibration and adjustments reduce positional error and improve positioning performance.
- Experimental testing will be conducted primarily in a controlled indoor desk or workspace environment.

### Delimitation of the Study

- The study is limited to a functional 3-DOF smart lamp prototype intended for indoor desk or workspace applications.
- The movement of the prototype is limited to Base Rotation (Yaw) 0°–350°, Elbow (Pitch): 30°–150°, Lamp-Head Tilt (Pitch): 45°–135°.
- The gesture-based control system is limited to a predefined set of hand gestures assigned to specific lamp movement commands. Sign-language recognition, full-body gestures, and autonomous user tracking are not included.
- The mobile-control system is limited to Bluetooth communication. Wi-Fi, Internet-based control, cellular communication, cloud control, and other long-distance communication methods are excluded.
- The gesture-based and Bluetooth mobile-control modes are limited to operate independently, and only one control mode will be active at a time. Simultaneous commands from both control modes will not be permitted.
- The study is limited to open-loop control and does not include continuous closed-loop position feedback or automatic position correction.
- Positional accuracy optimization is limited to an experimental trial-and-error calibration approach and does not include machine-learning-based optimization of the joint positions.
- Measurement of the actual joint angles is limited to the angular measuring instruments and methods selected for the experimental setup, such as a protractor, calibrated angular scale, or digital angle measuring device.
- The findings are limited to the specific hardware, mechanical structure, materials, and software configuration used in the developed prototype.
- The testing environment is limited primarily to a controlled indoor environment and does not include extreme outdoor or environmental conditions.
- The study focuses on positional accuracy, repeatability, execution of movement commands, and functional performance of the gesture and mobile control systems. Commercial manufacturing, mass production, industrial certification, long-term durability testing, and heavy-load robotic applications are outside the scope of the study.

## Significance of the Study [j][k]

This study is significant because it investigates the design, development, and experimental evaluation of a three-degree-of-freedom smart lamp that integrates vision-based hand-gesture control, Bluetooth-based mobile control, and servo-actuated positioning in a single system. The study also examines whether experimental calibration can reduce the difference between commanded and actual joint positions in an open-loop positioning system. Through repeated testing, the study is expected to provide measurable information regarding the positional accuracy, repeatability, and control reliability of the developed prototype.

The findings of this study will benefit the following:

**Users.** The created prototype might offer consumers a different, more practical way to change a desk lamp's position. When mobile operation is preferred or gesture-based control is inappropriate, the Bluetooth-based mobile application offers a backup control method. Gesture-based control uses predefined hand gestures to issue movement commands.

**Students.** Students studying embedded systems, computer vision, microcontroller programming, Bluetooth communication, servo motor control, mobile application development, and electromechanical system integration may find the study useful. It shows how these technologies can be incorporated into a working prototype and tested experimentally.

**Researchers.** Regarding the positioning performance of a multi-joint servo-actuated mechanism operating under open-loop control, the study might offer helpful experimental data. A useful method for analyzing positional error, repeatability, and the impact of calibration on a prototype system could be the use of externally measured and commanded joint angles.

**Future researchers.** Future research on gesture-controlled devices, robotic lighting systems, articulated mechanisms, multi-degree-of-freedom systems, and dual-mode control interfaces may use the results and methodology of this study as a guide. By adding additional sensing techniques, communication technologies, feedback mechanisms, control strategies, or more sophisticated calibration methods, future researchers may enhance the system.

**Field of Smart Lighting and Human–Device Interaction.** The study may also help to develop more interactive lighting systems by demonstrating the viability of combining natural gesture-based interaction with mobile control and motorized positioning. The findings may reveal useful information about the benefits and drawbacks of incorporating these technologies into an indoor smart-lamp application.

## Definition of terms [l]

Acronym

*(empty in source)*

---

# Chapter 2 — REVIEW OF RELATED LITERATURE AND STUDY [m][n][o][p][q][r][s][t][u]

## 2.1 Review of Related Literature

### 2.1.1 General Information

#### 2.1.1.1 Smart Lamp Systems

A smart lamp is a lighting device that integrates sensing, control, and communication technologies to provide functions beyond simple on-off switching. A recent design of relevance to the present study is the STM32-based intelligent desk lamp of Lian et al. (2021), which used an STM32F103C8T6 microcontroller together with light-intensity, distance, and pyroelectric sensor modules to provide automatic lighting, intelligent dimming, sitting-posture reminders, and wireless control through a cell phone application over a Bluetooth HC-05 module. The lamp operated in three modes: manual operation, intelligent dimming, and night-light operation, with Bluetooth mobile control available within the manual-control mode. In a similar study, Xu et al. (2023) designed a multi-functional desk lamp based on an STC89C52 microcontroller that combined infrared sensing, a photoresistor, and Bluetooth HC-05 remote communication to detect human sitting posture and ambient light and to adjust the brightness of the lamp adaptively, successfully achieving light-sensitive induction, human body sensing, and remote brightness control.

Hands-free and contactless control of lamps has also been explored in recent studies. Sulaiman et al. (2026) designed and implemented a hand gesture-based wireless control system for lamp and fan appliances in which a dedicated PAJ7620 infrared gesture sensor integrated with a transmitter ESP32 detected four predefined hand gestures and sent control commands through ESP-NOW to a receiver ESP32. In the prototype, an LED represented the lamp, and a relay primarily controlled the fan; the study reported successful functional demonstrations of gesture-to-output mapping, but it did not provide completed quantitative results for recognition accuracy or response time. Thakre et al. (2024) developed a voice-activated lamp system using an Arduino Nano, a Bluetooth module, and a single-channel relay, enabling remote lamp control through a dedicated mobile application using natural language voice commands. Although the system was limited to on-and-off switching and did not control lamp position or servo angles, it supports the use of Bluetooth mobile control as a convenient interface for lamps.

Beyond control interfaces, recent studies also demonstrate the automation of lamp positioning itself. Sun and Liu (2023) designed a 360° dead-angle-free smart desk lamp based on visual tracking, in which a convolutional neural network (CNN) algorithm was used to identify and locate target objects, and four servo motors were used to adjust the height and angle of the lamp head so that the light source could follow the target and provide dead-angle-free illumination. A camera and a rangefinder were integrated into the head of the desk lamp to capture images and determine the distance between the lamp head and the desktop, providing the basis for the servo adjustments. In testing, the CNN-based desk lamp demonstrated superior target recognition and positioning accuracy compared with support vector machine (SVM) and back-propagation neural network (BPNN) implementations, reporting a 0.54 mm average CNN localization error and approximately 0.53–0.56 mm tracking errors after stabilization. It should be noted that this error refers to the tracking and positioning of the lamp relative to the target object in millimeters, not to joint-angle error in degrees, which is the measure used in the present study. The Sun and Liu study is nonetheless strongly related to the present work at the mechanical level, because it demonstrates a servo-actuated desk lamp whose lamp head is positioned through a combination of motorized joints and camera vision. The present study differs in that it uses three servo joints, predefined hand gestures without machine learning, selectable gesture-based or Bluetooth control, open-loop positioning, and external angular measurement during testing.

The reviewed literature shows that smart-lamp systems have incorporated automatic dimming, presence detection, contactless interaction, Bluetooth mobile control, and automated positioning. However, limited work was identified within the reviewed literature that combines predefined gesture-based control, Bluetooth mobile control, and motorized multi-degree-of-freedom repositioning in a single physical smart-lamp system. Furthermore, the reviewed systems did not combine these functions with experimental open-loop servo-angle calibration. This gap supports the objective of the present study, which is to design and develop a hybrid gesture-based and mobile-controlled 3-DOF smart lamp and optimize its positional accuracy and repeatability through experimental calibration.

#### 2.1.1.2 Robotic Arm and Articulated Mechanisms

Robotic arms, also known as manipulators, are mechanical systems made up of interconnected joints and links that enable controlled movement of an end-effector or distal link. The links in a serial articulated mechanism are arranged in a sequential fashion from the base, and joints between neighboring links allow for movement. According to Zhang et al. (2023), an articulated robot is an open-chain structure made up of a number of links joined by joints, where each link's position is determined by the arrangement of the joints that came before it. In a similar vein, Antonov (2024) described how a sequence of links connected by actuated joints link the end-effector to the base in serial robotic manipulators.

The angular or linear displacement of each joint in an articulated mechanism determines the movement it produces. Actuators generate rotational movement that modifies the configuration of the connected links in mechanisms with revolute joints. The final position and orientation of the distal part of a serial mechanism are determined by the combined joint positions because the movement of one joint influences the position of the subsequent parts. Additionally, Antonov (2024) pointed out that although positioning errors from individual joints may accumulate toward the end of the kinematic chain, serial manipulators offer comparatively large workspaces and flexibility. When positional accuracy is a crucial performance requirement, this trait is especially pertinent.

Low-cost robotic systems have also used servo-actuated articulated mechanisms. Saini et al. (2023) used servo motors, an Arduino-based controller, computer-aided design, and kinematic analysis to create a three-degree-of-freedom robotic arm. Their system showed how a multi-joint mechanism's movement can be controlled by coordinating independently actuated joints. Systems where servo motors provide controlled rotational movement across multiple interconnected mechanical joints are relevant to the study.

Although the positioning structure of the suggested smart lamp is based on mechanical principles similar to a simplified serial articulated mechanism, it is not designed to operate as an industrial robotic arm. Three independently controlled servo-actuated joints generate the base rotation, elbow or arm pitch, and lamp-head pitch. The lamp head's final position and orientation are determined by the combined angular positions of these joints. Thus, the mechanical configuration, joint movement, workspace, and positional-accuracy assessment of the suggested 3-DOF smart lamp are all related to robotic-arm and articulated-mechanism design principles.

#### 2.1.1.3 Degree of Freedom

The number of independent motions or coordinates needed to characterize a mechanical system's configuration is known as its degree of freedom (DOF). The number of independent coordinates required to describe a mechanism's motion is its degree of freedom, according to López-Custodio and Müller (2022). As a result, a mechanism with three degrees of freedom has three independent motions that are controllable within the system's mechanical limitations.

Joints that connect the mechanism's individual links typically provide degrees of freedom in robotic manipulators. Prismatic joints offer translational motion, whereas revolute joints offer rotational motion. Typically, serial manipulators are made up of links joined by one-degree-of-freedom actuated joints; the mechanism's final configuration is determined by the sum of the individual joint motions (Antonov, 2024). Similarly, Vyas et al. (2025) described prismatic joints as offering translational motion and revolute joints as offering rotational motion, illustrating how the type of joint dictates the nature of a particular degree of freedom.

The number and allowable ranges of these joint movements influence the reachable workspace of a mechanism. Ceccarelli (2024) explained that the workspace of a manipulator represents the region that can be reached by a reference point at the extremity of the mechanism and that this workspace is determined by the mobility ranges of its joints. Therefore, increasing or changing joint movements can alter the positions and orientations that a mechanism can reach, while mechanical joint limits restrict its available workspace.

A three-degree-of-freedom robotic mechanism was demonstrated by Saini et al. (2023), who developed a 3-DOF robotic arm using servo-actuated joints and an Arduino-based controller. Their work illustrates the use of multiple independently controlled joints to produce coordinated mechanical positioning.

The base, elbow or arm, and lamp-head joints of the suggested smart lamp provide three rotational degrees of freedom. Base yaw rotation ranges from 0° to 350° in the first degree of freedom, elbow or arm pitch ranges from 30° to 150° in the second, and lamp-head pitch ranges from 45° to 135° in the third. The control system independently commands each joint, and the combined angular configurations of these joints determine the lamp head's final position and orientation. The defined angular limits limit each joint's range of motion, but they do not alter the mechanism's designation as a three-degree-of-freedom system.

### 2.1.2 OpenCV-Based Hand Gesture Control

Computer vision allows a system to interpret visual information captured from images or video. In hand-gesture recognition, a camera can serve as a contactless input device while image-processing techniques identify meaningful hand shapes and movements. Qi et al. (2024) describe the common stages of vision-based hand-gesture recognition as image acquisition, hand detection and segmentation, feature extraction, and gesture classification. Their review also discusses conventional techniques such as color-based segmentation, thresholding, contour analysis, and other feature-based methods. These approaches show that hand gestures can be recognized from visual characteristics without requiring the user to wear a physical input device.

Computer vision has also been used to control physical, servo-actuated mechanisms. Paterson and Aldabbagh (2021) developed a gesture-controlled robotic arm that used a USB camera and OpenCV to capture and process hand gestures. Their system applied image-processing operations such as color-space conversion, thresholding, erosion, dilation, and contour analysis before converting the detected hand information into commands. A Raspberry Pi then used these commands to control the robot's servo motors. Although the application was a robotic arm rather than a smart lamp, the control process is closely related to the present study because both use camera-based visual input to produce commands for servo-driven joint movement.

Gourob et al. (2021) presented a similar vision-based approach for controlling a robotic hand. Their system used a camera and OpenCV to process the hand region, detect contours, and examine geometric features such as the convex hull and convexity defects. Once a gesture was identified, the corresponding command was sent to an Arduino that actuated the servo motors of the robotic hand. This study is relevant because it demonstrates a rule-based method in which predefined hand gestures are converted into physical actuator commands without requiring machine learning as the main recognition approach.

Yime et al. (2023) also used Python and OpenCV to control the movement of a Delta robot through six predefined hand gestures. Each gesture represented a specific movement direction and was recognized using geometric characteristics of the hand. Their work is particularly relevant to the proposed smart lamp because it shows that a limited set of predefined gestures can be assigned to specific movement commands using conventional computer-vision processing. In the present study, the same general sequence will be followed: camera input, visual processing, predefined gesture identification, command generation, and servo-actuated lamp movement. Vision-based hand-gesture recognition will serve as the primary control method, while gesture-recognition reliability will remain a secondary performance measure because the main evaluation focuses on the positional accuracy and repeatability of the 3-DOF lamp mechanism.

### 2.1.3 Bluetooth-Based Mobile Control

Bluetooth is a short-range wireless communication technology that allows electronic devices to exchange data without requiring a physical wired connection. In microcontroller-based systems, Bluetooth communication can be used to transmit control commands from a mobile device to a controller, allowing a user to operate a system wirelessly within its communication range. In the study of Iadanza et al. (2023), they developed a robotic-arm system in which a mobile application communicated with an Arduino-based controller through an HC-05 Bluetooth module. The mobile application provided manual commands for controlling the movements of different servo motors, demonstrating the applicability of Bluetooth communication in using controlled robotic mechanisms remotely.

The HC-05 is a Bluetooth Serial Port Profile (SPP) module designed for wireless serial communication. It can interface with a microcontroller through Universal Asynchronous Receiver-Transmitter (UART) communication. Through this configuration, commands generated by a mobile application are transmitted wirelessly to the HC-05 module and forwarded to the microcontroller through serial communication. The microcontroller then interprets the received data and executes the corresponding programmed action.

In a mobile-control application, predefined buttons or commands may be assigned to specific movements or functions of a mechanism. When a user selects a command from the mobile application, the corresponding data is transmitted through Bluetooth and processed by the microcontroller, which then generates the required control signal for the actuator. This approach provides a direct method of manually controlling individual movements without requiring a wired controller.

In the proposed three-degree-of-freedom smart lamp, Bluetooth-based mobile control will provide an alternative control mode for commanding the base, arm, and lamp-head movements. The mobile application will transmit predefined commands through the HC-05 Bluetooth module to the microcontroller, which will interpret the received commands and control the corresponding servo motors. This control mode will operate separately from the gesture-based control mode.

### 2.1.4 Open-Loop Control System

Open-loop control is a control approach in which a system acts on a reference input or command without continuously using the measured output as feedback for automatic correction. Wang and Chortos (2022) explain that control without feedback can generally be classified as open-loop control. A key limitation of this approach is that the controller does not continuously verify whether the actuator has reached the desired state. In positioning applications, the controller therefore sends the required command based on the established behavior of the actuator, while any difference between the commanded and actual position is not automatically corrected during operation.

Open-loop positioning has been applied to physical robotic mechanisms in which actuator parameters are established through experimentation. Guo et al. (2022) developed an open-loop positioning method for an optical-fiber positioner robot and reported that feedback information did not need to be collected during the positioning operation. Instead, the driving parameters were adjusted experimentally, and the resulting positions were evaluated using a universal toolmaker's microscope. This is relevant to the present study because it shows that an open-loop positioning system can be tuned through testing and evaluated using an external measuring method without making that measurement part of the real-time control loop.

Runciman et al. (2021) likewise demonstrated open-loop position control in mechanisms with one, two, and three degrees of freedom. Their experiments repeatedly measured the physical positions of the mechanism and evaluated positioning error and repeatability even though continuous corrective position feedback was not used during operation. Their results showed that repeated paths could be reproduced, although measurable offsets and errors were still present. While their system used soft hydraulic actuators rather than servo motors, the study supports an important principle for the present capstone: an open-loop multi-DOF mechanism can be evaluated by comparing desired and measured movement and by examining its consistency across repeated trials.

These findings support the control and evaluation approach of the proposed 3-DOF smart lamp. A gesture or Bluetooth command will specify the desired joint movement, the controller will send the corresponding command to the servo motor, and the joint will move without continuously returning an independent measurement of its actual position for automatic correction. Factors such as servo characteristics, mechanical alignment, structural loading, zero-reference settings, command-to-angle mapping, power conditions, and calibration may influence the resulting position; however, they will be treated only as possible factors until they are examined through experimental testing. During testing, the actual joint angles will be measured externally and compared with the commanded target angles. The resulting positional error and repeated measurements will be used to evaluate positional accuracy and repeatability and to guide trial-and-error calibration. Because these measurements are used for evaluation and offline adjustment rather than continuous real-time correction, the system remains open-loop during normal operation.

### 2.1.5 Positional Accuracy and Positional Error

Positional accuracy describes how closely a mechanical or robotic system can reach its intended or commanded position. In mechanisms driven by servo motors, the final position of a joint may not exactly match the commanded angle because of factors such as mechanical tolerances, actuator limitations, backlash, misalignment, variations in load, and improper calibration. These differences between the intended and actual positions are generally considered positional or angular errors and are important indicators of the system's positioning performance.

Matilla et al. (2023) examined this concept through a three-degree-of-freedom robotic wrist by comparing the intended angular positions with the actual movements produced by the mechanism. Their findings showed measurable differences in pitch, yaw, and roll, indicating that a commanded angle does not always result in an exact physical position. In a similar manner, Suryadarma et al. (2025) assessed the positioning accuracy and repeatability of an Arduino-based robotic arm operating under an open-loop control system. Their study highlighted the need for experimental position measurement because an open-loop controller does not continuously monitor the actual output or automatically correct deviations during operation.

Positional error is determined by the difference between the target or commanded position and the actual position achieved by the mechanism. Sutisna et al. (2022) found quantifiable errors in an Arduino-based robotic arm that was managed by a mobile application; according to their research, servo commands may result in minor departures from the desired physical position. Additionally, Kiswanto et al. (2021) showed that recognizing these positioning errors and implementing appropriate compensation can significantly lower the ensuing deviation. This demonstrates how calibration and adjustment can help servo-driven robotic systems perform better in terms of position.

In the present study, positional accuracy is used to assess how closely each of the three servo-controlled joints of the smart lamp reaches its assigned angular position. Since the proposed system operates using an open-loop control configuration, the actual joint position is not continuously measured and returned to the controller for automatic correction. Instead, the actual angle reached by each joint will be measured externally during experimental testing and compared with its corresponding commanded angle. The difference between these values will represent the positional error of the joint. The resulting measurements will then be used as a basis for calibration and adjustment of the servo commands to minimize positioning deviations and improve the overall positional accuracy of the three-degree-of-freedom smart lamp.

### 2.1.6 Servo Position Calibration

Calibration is an important process in robotic positioning because differences can occur between the position commanded by a control system and the position actually produced by the mechanical system. Kana et al. (2022) explained that manufacturing and assembly variations, particularly joint offsets, can contribute to positional inaccuracies in robotic mechanisms. Their work on robotic-arm recalibration showed that compensating for joint and link-related deviations can reduce positioning error and improve the accuracy of the resulting robot model.

For servo-driven mechanisms, a commanded servo angle does not necessarily correspond perfectly to the actual mechanical angle of the attached joint. Differences may result from servo characteristics, mounting alignment, mechanical tolerances, joint offsets, or the relationship between the control command and the physical mechanism. Consequently, calibration may be performed by comparing commanded positions with measured actual positions and determining the correction necessary to reduce their deviation. Robot-calibration research similarly uses differences between nominal or commanded positions and measured positions to identify errors and apply corrections intended to improve absolute positioning accuracy.

In the proposed three-degree-of-freedom smart lamp, servo position calibration will be used to improve the positional accuracy of the base, arm, and lamp-head joints. During experimental testing, selected angular positions will be commanded and the actual joint positions will be measured externally.

## 2.2 Review of Related Studies

### 2.2.1 2-in-1 Motion and Sound Powered Desk Lamp

Flipping on a light switch may be considered a common act among most people, but there are some who find it extremely difficult to perform such an act. Such an ordeal became the motivation for Adam et al. (2023) to develop a desk lamp which turns on through motion and sound. An Arduino microcontroller was programmed to handle the detection, and quantitative observation was used throughout the testing. The device came out excellent in both sensitivity ratings. It recognized five hand motions, namely back-and-forth vertical and horizontal handwave motions, raising the front and back parts of the hand, pushing the palm towards the sensor, and a peace-sign hand gesture, as well as three sound sources (handclap, knocking, and tapping an object). Of all the papers in this subsection, theirs is the one that operates most like the proposed lamp, since the entire purpose of the device is that hand movements alone switch the light, with no switch in the way. The common ground ends there, though. Their lamp senses motion and sound through direct detectors, while the proposed lamp reads gestures from camera frames instead. Theirs also stays put, doing no more than turning the light on or off, whereas the lamp proposed here is meant to sweep its head across three servo-driven joints.

### 2.2.2 Hand Gesture Recognition for Filipino Sign Language Under Different Backgrounds

Ang et al. (2022) aimed to investigate the capabilities of hand gesture recognition on a Raspberry Pi, a device that is significantly less powerful than a computer in terms of processing power. The selected task involved Filipino Sign Language (FSL) In their pipeline, YOLO-Lite first located the hand inside the frame and MobileNetV2 then sorted the gesture into one of 26 letters, and the setup averaged 93.29% accuracy while holding up in cluttered backgrounds. Not every letter came easily: Q, J, and Z were difficult, and N was sometimes interpreted as M. For the proposed lamp, the value of the paper lies mainly in the hardware lesson: vision-based gesture recognition is workable on the same class of single-board computer that the gesture mode of the lamp relies on. The resemblance thins out at the output stage. Their recognizer ends at a letter label, whereas the lamp must end at a servo command, and their approach leans on trained machine-learning models, a step the present study skips entirely in favor of predefined gestures and simpler classification.

### 2.2.3 Improvement of Trajectory Errors on Remote-Controlled Differential Drive Robot via Mobile-based GUI through Bluetooth Connection

It is easy to assume that the controller has nothing to do with how precisely a machine moves, but Dimalanta et al. (2023) of the University of Santo Tomas showed otherwise. The system was implemented using a remotely controlled differential drive service robot, which was run using linear and rotational trajectories with 5 different speeds ranging between 0.75 m/s and 0.15 m/s. At times, the operator would use the remote joystick to operate the robot, while in other cases, the same trajectories would be followed using a phone application connected via Bluetooth connection, allowing comparison of both interfaces to be done. The phone-to-robot interface proved superior; the trajectory errors were 50%-60% lower than those done using the joystick interface. Two lessons carry over to the smart lamp. For one, a machine can be commanded wirelessly from a mobile device, which is exactly how the Bluetooth mode of the lamp works, and the experiment even suggests such control can tighten positioning rather than loosen it. For another, the study evaluates its system the same way the proposed study will evaluate the lamp, by measuring the gap between the path commanded and the path actually traced. The objects under control, of course, could hardly be more different: a robot rolls across a floor and its deviation is quoted in distance, while a lamp rotates joints and its deviation will be quoted in degrees of angle.

### 2.2.4 Filipino Sign Language Hand Gesture Recognition Using MediaPipe and Machine Learning

A second team in Cebu, Pilare et al. (2024) of the University of San Jose-Recoletos, pursued the same recognition problem along a different technical route. MediaPipe is their feature extractor, tracing the hands through every frame of a webcam video, and a Long Short-Term Memory (LSTM) network takes over afterwards, reading the sequence of traced landmarks as a whole and assigning it to one of three basic words or twenty-seven phrases. Training ran on 900 samples of thirty frames each; the best results reached 98.41% on training and 98.89% on testing. What this means for the present work is mostly reassurance: ordinary camera video of deliberate hand gestures can be classified with very high reliability, which is the assumption the gesture input of the lamp rests on. Direct comparison is limited, though. Their classifier runs on a desktop computer rather than embedded hardware, its output is text on a screen rather than a command to motors, and it depends heavily on machine learning, in contrast with the rule-based gesture set of the proposed lamp.

### 2.2.5 Comparative Analysis of Different Systematic Odometry Error Correction Methods on a Differential Drive Indoor Service Robot

Robots rarely arrive exactly where their controllers intend them to, and Pangaliman et al. (2022) of the University of Santo Tomas studied how much of that error can be corrected. Their indoor service robot, fitted with wheel odometry and a 2D LiDAR, was calibrated using three methods of systematic odometry error correction: UMBmark, Lee's method, and Jung's method. All three ran through the Bidirectional Square Path test under the Robot Operating System. Jung's method proved the most suitable, improving dead-reckoning accuracy by 20.4% relative to the uncalibrated robot. Just as interesting was the error that would not go away. Slippage, being nonsystematic, continued to distort the robot's return position, and the authors suggested redesigning the wheelbase to lessen its effect. For the present study, this paper serves as a methodological background. It demonstrates locally that the positioning error of a controlled mechanism is composed of systematic and nonsystematic parts, and that the systematic part responds well to measurement and calibration. The techniques themselves do not transfer, since odometry correction differs from servo calibration, but the underlying practice, checking the actual position against the commanded position, is exactly the practice that the angular accuracy testing of the smart lamp will follow.

### 2.2.6 Accuracy Test of an Open-Loop Control System for Arduino-Based Robotic Arms with a PLA+ 3D-Printed Body for Repetitive Tasks

According to Suryadarma et al. (2025), an Arduino-based robotic arm with an open-loop control system was developed and evaluated to determine its accuracy and repeatability in performing repetitive tasks. The robotic arm utilized a PLA+ 3D-printed structure, which provided a lightweight and durable framework suitable for repeated operation. The researchers selected PLA+ because of its favorable mechanical properties, ease of fabrication, and suitability for producing cost-effective robotic components.

The system employed an Arduino Mega as its main controller and utilized stepper motors to control the movement of the robotic arm. The robotic arm consisted of three degrees of freedom (3-DOF) together with a translational rail mechanism. Since the system used an open-loop control approach, it operated without continuous positional feedback. This configuration reduced the hardware requirements and complexity of the system; however, the absence of real-time feedback limited its ability to automatically detect and correct positional errors during operation.

To evaluate the accuracy and repeatability of the robotic arm, Suryadarma et al. (2025) conducted 30 repetitive trials in which the arm moved between predefined positions. The robotic arm traveled a distance of 500 mm, while the difference between the programmed target position and the actual position reached by the end effector was measured. The results showed that the positional bias generally ranged from approximately 0 to 1.2 mm, with a mean bias of approximately 0.593 mm. The statistical results also indicated that there were no significant trends or oscillations in the recorded positional errors throughout the trials.

The findings demonstrate that an Arduino-based robotic arm using an open-loop control system can achieve reasonable accuracy and repeatability when performing predefined repetitive movements under controlled conditions. However, the researchers emphasized that further improvements are necessary to enhance its precision and consistency. Furthermore, because an open-loop system lacks real-time feedback, its ability to respond to external disturbances or changing operating conditions remains limited. The study therefore provides useful evidence that Arduino-based robotic arms can serve as practical and cost-effective platforms for repetitive tasks while also emphasizing the importance of feedback mechanisms when greater accuracy and adaptability are required.

### 2.2.7 Gesture-Based Robotic Control (2022)

Wen et al. (2022) developed a gesture-controlled robotic arm capable of replicating movements performed by a human operator. The system used accelerometers, an MPU6050 motion sensor, two Arduino Mega microcontrollers, servo motors, and NRF24L01 wireless communication modules.

The motion sensors detected the movement of the user's arm and transmitted the corresponding data to the robotic system. These signals were then used to control the robotic arm's joints, allowing the system to reproduce the user's gestures without direct physical contact.

The study is relevant to the present research because both systems use gesture-based interaction to control electromechanical devices. However, Wen et al. (2022) used wearable sensors, while the proposed smart lamp uses camera-based gesture recognition.

In the proposed system, detected hand gestures are processed and converted into commands that control the movement of the lamp's joints. The study therefore supports the feasibility of using gesture-based control for a three-degree-of-freedom smart lamp, particularly for contactless positioning and adjustment.

### 2.2.8 Mobile-Controlled Servo Positioning (2025)

Alsayaydeh et al. (2025) developed a five-degree-of-freedom robotic arm controlled through a mobile application. The system used an Arduino Mega 2560, MG996R servo motors, and an HC-05 Bluetooth module for wireless communication.

The mobile application was created using MIT App Inventor and provided buttons and sliders for controlling individual joints. This allowed users to adjust the position and movement of each servo motor through a wireless interface.

The researchers evaluated the positional accuracy of the robotic arm by comparing the commanded angles with the actual measured angles. For instance, a target shoulder angle of 150° resulted in an actual position of 143°, while a target elbow angle of 180° resulted in 168°.

The system achieved an overall accuracy of approximately 94.67%. The observed differences were attributed to factors such as servo limitations, mechanical construction, and system calibration.

This study is relevant to the proposed smart lamp because both systems use mobile-based control, Bluetooth communication, a microcontroller, and servo motors for positional adjustment. Although the robotic arm operates with five degrees of freedom, its control and accuracy-testing approach can also be applied to the proposed three-degree-of-freedom smart lamp.

### 2.2.9 Open-Loop Multi-DOF Positioning (2025)

A 2025 study developed RoboVR, a low-cost four-degree-of-freedom robotic arm controlled through an Arduino-based open-loop system. Joint-angle commands were converted into pulse-width modulation (PWM) signals to drive the servo motors. Since the system lacked positional feedback, the researchers compared the commanded joint angles with the actual servo positions during testing.

The results showed varying positional errors across the joints. Average errors of approximately −1.60° and 1.8° were observed during basic movements, while an individual elbow movement produced an average error of about 1.43°. Greater deviations were also reported in the shoulder joint, demonstrating that open-loop control may produce differences between the intended and actual positions.

This study is relevant to the proposed three-degree-of-freedom smart lamp because it also employs an open-loop positioning approach. Comparing the commanded and measured joint angles can be used to determine positional errors and identify necessary calibration adjustments, thereby supporting the evaluation of the smart lamp's movement accuracy.

### 2.2.10 Position Accuracy Optimization (2021)

Created a control system for a robotic-arm manipulator that used an Arduino Mega 2560 to control servo and stepper motors. The computed joint values were sent to the actuators using commands made with the Arduino IDE. During testing Kiswanto et al. found positioning inaccuracies in three servo motors with differences of about 16.471%, 1.463% and 0.588%. After error compensation was applied the reported errors fell to 0.003%, 0.143% and −0.382%. Kiswanto et al. also checked the consistency of the mechanism and found that the control system could place the end effector closer to the target once the adjustments were made. This research supports the improvement of accuracy for the proposed smart lamp. Likewise the current study will identify the differences between the commanded positions and those measured externally for the three servo-controlled joints. The detected errors can then serve as a basis for the calibration and modification of the servo commands. By carrying out tests and calibrations Kiswanto et al. aim to reduce angular differences and improve the positioning precision of the lamp all while keeping the open-loop control setup.

## 2.3 Synthesis of Study

### 2.3.1 Root Causes of the Problem

To identify the possible factors that may contribute to the positional inaccuracy and overall control performance of the proposed three-degree-of-freedom (3-DOF) smart lamp, the researchers performed a root cause analysis using an Ishikawa or Fishbone Diagram. Potential factors related to the user, method, machine, material, measurement, and environment were identified. These candidate causes will be examined using related literature, previous studies, technical evidence, and later experimental testing before they are treated as confirmed causes of the identified problem.

#### 2.3.1.1 Fishbone Diagram of the Study [v][w][x]

Figure 2.X presents the Ishikawa or Fishbone Diagram used to identify possible factors that may contribute directly or indirectly to the positional inaccuracy of the 3-DOF smart lamp. The potential causes were grouped according to the user, method, machine, material, measurement, and environmental conditions involved in the operation and testing of the prototype. Some factors are related directly to the physical positioning of the servo-actuated joints, while others mainly affect gesture recognition and the proper generation of movement commands.

[figure — in source doc only]

**Figure 2.5 Fishbone/Ishikawa Diagram of the Study**

To conclude, below are the candidate root causes identified in the study.

- Root Cause No. 1: Suboptimal Hand-Gesture Execution and Recognition
- Root Cause No. 2: Hand-to-Lamp/Camera Distance
- Root Cause No. 3: Servo and Control Parameters
- Root Cause No. 4: Camera View Obstruction/Occlusion
- Root Cause No. 5: Workspace Lighting and Visual Conditions
- Root Cause No. 6: Prototype Repositioning/Portability
- Root Cause No. 7: Insufficient Structural Stiffness and Joint Support

### 2.3.2 Root Cause Validation Summary [y]

| # | Root Cause Description | Root Cause Validation Process | Validation |
| --- | --- | --- | --- |
| 1 | Suboptimal Hand-Gesture Execution and Recognition | Review of Related Study<br>• Fauzan et al. (2024)<br>Study: One-Phase Smart Switch using OpenCV Hand Gesture Recognition<br>Data:<br>• Average classification accuracy = 0.96; average F1-score = 0.90.<br>• At 0° hand tilt, all tested gestures reached 100% recognition. At 60°, the five-finger gesture decreased to 64%.<br>• Qi et al. (2024) identifies hand posture, segmentation, and recognition variability as challenges in vision-based hand-gesture systems.<br>Connection to the present study:<br>Unclear or poorly oriented gestures may result in failed or incorrect command recognition. The effect is indirect because it occurs before the correct servo command is issued. | VALID |
| 2 | Hand-to-Lamp/Camera Distance | Review of Related Study<br>• Fauzan et al. (2024)<br>Study: One-Phase Smart Switch using OpenCV Hand Gesture Recognition<br>Data:<br>• All tested gestures achieved 100% recognition at 30 cm and 60 cm.<br>• At 150 cm, individual results ranged from 88% to 93%; at 180 cm, results ranged from 77% to 82%.<br>• Qi et al. (2024) also identifies camera-to-user distance as an important factor in hand segmentation.<br>Connection to the present study:<br>Distance can change the apparent size and visibility of the hand in the camera frame, affecting gesture reliability and command generation rather than the physical accuracy of a correctly commanded servo. | VALID |
| 3 | Servo and Control Parameters | Review of Related Literature and Study<br>• Kana et al. (2022)<br>Study: Fast Kinematic Re-Calibration for Industrial Robot Arms<br>Data:<br>• Joint offsets introduced during manufacturing and assembly are identified as an underlying source of position inaccuracy in more than 90% of the situations discussed in their calibration context.<br>• Kiswanto et al. (2021)<br>Study: Development of Robotic Arm Manipulator Control System for Micromilling Tool Wear Monitoring Based on Computer Vision<br>Data:<br>• Servo 1, 2, and 3 errors were reported as 16.471%, 1.463%, and 0.588%. After compensation, the reported values decreased to 0.003%, 0.143%, and -0.382%.<br>Connection to the present study:<br>This directly supports testing servo calibration, zero-reference positions, and command-to-angle mapping in the open-loop smart lamp. | VALID |
| 4 | Camera View Obstruction / Occlusion | Review of Related Literature<br>• Qi et al. (2024)<br>Study: Computer Vision-Based Hand Gesture Recognition for Human-Robot Interaction: A Review<br>Data / Finding:<br>• Occlusion, complex hand posture, segmentation difficulty, and background conditions are identified as challenges in vision-based gesture recognition.<br>• Bakheet and Al-Hamadi (2021)<br>Study: Robust Hand Gesture Recognition Using Multiple Shape-Oriented Visual Cues<br>Data / Finding:<br>• The study describes self-occlusion among fingers as an inherent difficulty in vision-based hand-pose estimation.<br>Connection to the present study:<br>Obstruction can prevent the system from identifying the intended predefined gesture and therefore may cause a missing or incorrect movement command. The effect is indirect. | VALID |
| 5 | Workspace Lighting and Visual Conditions | Review of Related Study<br>• Fauzan et al. (2024)<br>Study: One-Phase Smart Switch using OpenCV Hand Gesture Recognition<br>Data:<br>• At 40 lux, individual recognition results ranged from 97% to 99%.<br>• At 70 lux, all tested gestures reached 100% recognition.<br>• Qi et al. (2024) also discusses illumination changes and complex backgrounds as conditions that can make segmentation and recognition more difficult.<br>Connection to the present study:<br>Lighting and visual background conditions can affect the camera-based primary control mode. They influence command recognition rather than directly changing the mechanical accuracy of the servo joints. | VALID |
| 6 | Prototype Repositioning / Portability | Review of Current Study and Related Literature<br>• Present study scope and delimitation<br>Data / Study Condition:<br>• The smart lamp is intended for a controlled indoor desk or workspace environment.<br>• Positional accuracy, repeatability, gesture reliability, Bluetooth reliability, and response time are identified as performance measures; portability is not identified as a measured performance variable.<br>• Related gesture literature shows that moving the setup can change distance, viewing angle, occlusion, lighting, and background conditions, but these effects are already represented by Root Causes 2, 4, and 5.<br>Validation decision:<br>Current evidence does not establish portability by itself as an independent cause of servo positional inaccuracy. It should only be treated as a candidate until prototype testing demonstrates an independent effect.. | INVALID |
| 7 | Insufficient Structural Stiffness and Joint Support | Review of Related Literature<br>• Jiao et al. (2022)<br>Study: Variable Stiffness Identification and Configuration Optimization of Industrial Robots for Machining Tasks<br>Data / Finding:<br>• The study states that low structural stiffness significantly affects robot positional accuracy and reports that industrial-robot stiffness is only about 2% to 5% of CNC-machine stiffness.<br>• Liu et al. (2022)<br>Study: Deflection Estimation of Industrial Robots with Flexible Joints<br>Data / Finding:<br>• Positioning accuracy is described as susceptible to load and motion when robot stiffness is insufficient because joint and link deflection can occur.<br>Connection to the present study:<br>This directly supports examining joint looseness, structural loading, sag, insufficient stiffness, and mechanical alignment as possible contributors to measured joint-position deviation. | VALID |

#### 2.3.2.1 Root Cause No. 1: Suboptimal Hand-Gesture Execution and Recognition

The gesture-control mode depends on the user presenting a predefined hand gesture that can be clearly captured and interpreted by the camera-processing system. Fauzan et al. (2024) evaluated an OpenCV-based hand-gesture lighting controller and reported an average classification accuracy of 0.96 and an average F1-score of 0.90. Their tilt-angle test showed 100% recognition for all tested gestures at 0°, while recognition decreased as the hand was tilted, including a decrease to 64% for the five-finger gesture at 60°. Qi et al. (2024) similarly identifies hand posture, segmentation, and gesture characteristics as important challenges in vision-based recognition.

For the proposed smart lamp, this evidence supports suboptimal gesture execution and recognition as a valid indirect root cause. A poorly presented gesture may result in no command or an incorrect command. However, after the correct joint-angle command has already reached the servo, gesture execution no longer determines the physical positioning accuracy of that joint.

#### 2.3.2.2 Root Cause No. 2: Hand-to-Lamp/Camera Distance

The distance between the user's hand and the camera affects how large and clear the hand appears in the captured frame. Fauzan et al. (2024) reported 100% recognition for all tested gestures at 30 cm and 60 cm. At 150 cm, the individual results ranged from 88% to 93%, while at 180 cm they ranged from 77% to 82%. Qi et al. (2024) also identifies camera-to-user distance as an important factor in hand segmentation.

This root cause is therefore valid as an indirect factor for the proposed lamp. An unsuitable operating distance may make gesture recognition less reliable and may prevent the intended movement command from being generated. It should not be described as a direct mechanical cause of servo-angle error.

#### 2.3.2.3 Root Cause No. 3: Servo and Control Parameters

The positioning of the smart lamp depends on the relationship between the angle commanded by the controller and the angle physically reached by each servo-driven joint. Kana et al. (2022) explains that manufacturing and assembly errors, particularly joint offsets, are an important source of robot-positioning inaccuracy. Kiswanto et al. (2021) reported servo errors of 16.471%, 1.463%, and 0.588% before compensation. After error compensation, the reported values decreased to 0.003%, 0.143%, and -0.382%.

These findings closely support the present study because its open-loop calibration process includes servo calibration, zero-reference adjustment, angle mapping, and comparison of commanded and externally measured positions. Servo and control parameters are therefore considered a valid direct root cause of positional inaccuracy.

#### 2.3.2.4 Root Cause No. 4: Camera View Obstruction / Occlusion

Camera obstruction occurs when the hand or important hand features cannot be clearly observed by the vision system. Qi et al. (2024) identifies occlusion, complex posture, background conditions, and segmentation difficulty as recurring challenges in vision-based hand-gesture recognition. Bakheet and Al-Hamadi (2021) likewise describe self-occlusion among the fingers as an inherent difficulty in hand-pose estimation.

For the proposed smart lamp, an obstructed or partially hidden hand can reduce the reliability of predefined-gesture recognition and may result in a missing or incorrect command. The root cause is valid, but its effect is indirect because it acts on the gesture-input stage rather than directly on the servo's physical positioning.

#### 2.3.2.5 Root Cause No. 5: Workspace Lighting and Visual Conditions

Lighting and visual background conditions can influence the quality of camera-based hand-gesture recognition. Fauzan et al. (2024) tested recognition under two lighting levels and reported individual accuracy values of 97% to 99% at 40 lux, compared with 100% for all tested gestures at 70 lux. Qi et al. (2024) also discusses changes in illumination and complex backgrounds as conditions that can make hand detection and segmentation more difficult.

This factor is valid for the gesture-control subsystem of the smart lamp because the primary control method depends on camera input. The effect should be described as indirect: poor visual conditions may interfere with recognizing the correct command, but they do not by themselves prove

#### 2.3.2.6 Root Cause No. 6: Prototype Repositioning / Portability

The Fishbone Diagram identifies prototype repositioning or portability as a possible factor. However, the current scope of the study is limited primarily to a controlled indoor desk or workspace environment, and portability is not identified as one of the primary or secondary performance measures. Moving the prototype may indirectly change the hand-to-camera distance, camera viewpoint, lighting, background, or setup geometry, but those conditions are already represented by other candidate root causes.

Based on the present literature and project scope, portability by itself is not yet validated as an independent cause of positional inaccuracy. It should remain a candidate factor only until experimental testing shows that repositioning the prototype produces a measurable effect that cannot be explained by distance, occlusion, lighting, or mechanical setup changes.

#### 2.3.2.7 Root Cause No. 7: Insufficient Structural Stiffness and Joint Support

The physical structure of a multi-joint mechanism can affect the position actually reached by the system. Jiao et al. (2022) states that low structural stiffness significantly affects robot positional accuracy and notes that the stiffness of industrial robots is only about 2% to 5% of that of CNC machines. Liu et al. (2022) similarly explains that robot positioning accuracy is susceptible to load and motion when stiffness is insufficient because deflection can occur in the joints and links.

The same mechanical principle is relevant to the 3-DOF smart lamp. Structural loading, joint looseness, sag, insufficient stiffness, or misalignment may cause the actual lamp-joint position to differ from the commanded angle. This is therefore considered a valid direct root cause, although its actual contribution must still be measured using the developed prototype.

### 2.3.3 Solution Validation Summary

| # | Solution Description | Solution Validation Process | Validation |
| --- | --- | --- | --- |
| 1 | Standardized Predefined Hand Gestures | Literature-Based Solution:<br>Qi et al. (2024) identifies gesture characteristics, hand posture, occlusion, and segmentation as factors that affect visual hand-gesture recognition.<br>Yime et al. (2023) demonstrated the use of a limited set of predefined hand gestures based on geometric hand characteristics. The proposed solution is to use a small set of clearly distinguishable gestures and validate them through repeated recognition trials to determine whether each gesture consistently produces the intended movement command. | VALID |
| 2 | Establishment of an Appropriate Hand-to-Camera Operating Distance | Literature-Based Solution:<br>Qi et al. (2024) identifies camera-to-user distance as an important factor in hand segmentation. The proposed solution is to establish a practical operating distance in which the complete hand remains clearly visible within the camera frame. Validation will involve repeated gesture-recognition trials at selected distances and comparison of the resulting recognition reliability. | VALID |
| 3 | Servo Position and Control Parameter Calibration | Technical Solution:<br>Bilancia et al. (2022) identifies servo mechanisms in robot joints as an important source of positioning error, while Kana et al. (2022) shows that joint offsets and manufacturing or assembly variations may be reduced through recalibration. The proposed solution is to calibrate zero-reference settings, servo limits, and command-to-angle mapping. Target and externally measured actual angles will be compared before and after calibration to determine whether positional error and repeatability improve. | VALID |
| 4 | Maintaining an Unobstructed Camera View | Literature-Based Solution:<br>Qi et al. (2024) identifies hand and finger occlusion as a major challenge in computer-vision gesture recognition. The proposed solution is to position the camera and define an interaction area that keeps the user's hand visible during gesture execution. Repeated gesture trials will be used to determine whether the selected camera placement reduces failed or incorrect command recognition caused by obstruction. | VALID |
| 5 | Controlled Workspace Lighting and Visual Conditions | Literature-Based Solution:<br>Qi et al. (2024) reports that lighting inconsistencies and background irregularities can affect hand segmentation and gesture recognition. The proposed solution is to use adequate and reasonably consistent indoor lighting with a manageable visual background. Gesture-recognition trials under selected workspace conditions will be compared to identify conditions that provide more stable command recognition. | VALID |
| 6 | Standardized Prototype Placement and Setup Geometry | Design-Control Solution: Although portability itself was not established as an independent root cause, the root-cause analysis identified that repositioning can change already validated conditions such as hand-to-camera distance, camera viewpoint, workspace lighting, and measurement geometry. The proposed solution is to use fixed placement and alignment references for the lamp, camera, and experimental setup. This is a valid experimental-control measure because it reduces setup variation and keeps the validated operating and measurement conditions consistent during repeated trials. | VALID |
| 7 | Improved Structural Stiffness and Joint Support | Technical Solution:<br>Jiao et al. (2022) reports that low structural stiffness significantly affects robot positional accuracy, while Liu et al. (2022) explains that loading and insufficient stiffness can cause joint and end-effector deflection. The proposed solution is to ensure proper joint tightness, servo mounting, structural support, and controlled loading. Positional error and repeatability will be compared before and after necessary mechanical adjustments or reinforcement. | VALID |

#### 2.3.3.1 Solution No. 1: Standardized Predefined Hand Gestures

The gesture-based control system depends on the user's hand configuration being visible and sufficiently clear for the vision-processing software to identify it correctly. Since the root-cause validation identified suboptimal hand-gesture execution and recognition as a valid indirect factor, the proposed solution is to establish a limited set of predefined gestures that are easy to distinguish and perform consistently.

Qi et al. (2024) explains that vision-based hand-gesture recognition involves stages such as detection, segmentation, feature extraction, and classification, and that complex hand postures and occlusion can interfere with reliable recognition. Yime et al. (2023) also demonstrated the use of six specific hand gestures identified through geometric hand characteristics and assigned to robot movements. These findings support the use of a controlled and clearly defined gesture set for the proposed smart lamp.

For solution validation, each predefined gesture will be performed repeatedly under the selected operating conditions, and the researchers will record whether the intended movement command is generated. Gestures that frequently produce failed or incorrect recognition may be revised or their image-processing parameters adjusted. This solution is intended to improve gesture-recognition reliability and command execution; it does not directly correct the physical positional error of a servo after the correct command has already been received.

#### 2.3.3.2 Solution No. 2: Establishment of an Appropriate Hand-to-Camera Operating Distance

The root-cause validation identified hand-to-lamp or camera distance as a valid indirect factor because the distance between the user's hand and the camera affects how clearly the hand can be captured for visual processing. The proposed solution is to establish a practical operating distance in which the complete hand remains visible and contains sufficient visual information for recognition.

Qi et al. (2024) identifies camera-to-user distance as an important factor in hand segmentation. Excessive distance can reduce the amount of useful hand information captured by the camera, while excessively close positioning can cause portions of the hand to move outside the camera frame or become partially occluded.

To validate the solution, the predefined gestures will be tested at several practical distances while other conditions are kept as consistent as possible. The recognition results will be compared to identify a suitable interaction range. The selected range will then be used during the main gesture-control tests of the smart lamp.

#### 2.3.3.3 Solution No. 3: Servo Position and Control Parameter Calibration

Servo and control parameters are directly related to the positional-accuracy objective of the proposed 3-DOF smart lamp. The root-cause validation identified servo characteristics, zero-reference settings, calibration values, joint offsets, and command-to-angle mapping as relevant factors that may cause the actual joint position to differ from the commanded target angle.

Bilancia et al. (2022) identifies servo mechanisms used in robot joints as an important source of positioning error. Kana et al. (2022) likewise explains that differences between ideal and actual robot geometry, including joint offsets caused by manufacturing and assembly, can contribute to positional inaccuracy and may be addressed through recalibration. These findings support calibration as the primary proposed solution for the direct servo and control parameter root cause.

During validation, selected target angles will be commanded for the base, elbow or arm, and lamp-head joints. The actual joint angles will then be measured externally and compared with their target values. Based on the measured differences, adjustments may be made to the zero-reference position, servo limits, calibration values, or command-to-angle mapping. The same target angles will be tested again to determine whether positional error is reduced and repeatability is improved. Because external measurements are used for experimental evaluation and offline calibration rather than continuous automatic correction, the system remains open-loop during normal operation.

#### 2.3.3.4 Solution No. 4: Maintaining an Unobstructed Camera View

Camera view obstruction or occlusion may prevent the gesture-control subsystem from correctly observing the user's hand. Since the root-cause validation identified camera obstruction as a valid indirect factor, the proposed solution is to position the camera and define an interaction area that keeps the hand sufficiently visible during gesture execution.

Qi et al. (2024) identifies hand and finger occlusion as an important challenge in vision-based gesture recognition. Overlapping fingers, objects in front of the hand, or movement outside the useful camera view can interfere with detection and segmentation and may prevent the intended command from being generated.

The solution will be evaluated through repeated gesture-recognition trials using the selected camera position and interaction area. The researchers will observe whether obstruction, overlapping fingers, or movement near the edge of the camera view causes failed or incorrect commands. The camera position and user interaction area may then be adjusted to reduce these recognition problems.

#### 2.3.3.5 Solution No. 5: Controlled Workspace Lighting and Visual Conditions

The root-cause validation narrowed the broader room-conditions factor to workspace lighting and visual conditions because these are the environmental elements supported by the reviewed literature. The proposed solution is to maintain adequate and reasonably consistent indoor lighting and a manageable visual background during gesture-control testing.

Qi et al. (2024) discusses how lighting inconsistencies, complex backgrounds, and other visual conditions can interfere with hand segmentation and gesture recognition. For the proposed smart lamp, these conditions may affect whether the correct gesture command is generated, although they do not directly determine the physical angle reached by a servo after a correct command is received.

To validate the solution, the predefined gestures will be tested under selected practical indoor lighting and background conditions. Recognition results will be compared to identify conditions that provide more consistent gesture detection. The selected workspace conditions will then be maintained as consistently as possible during the main experimental testing. Ordinary room temperature and ventilation are not included in this solution because the current root-cause validation did not establish them as important factors for the prototype.

#### 2.3.3.6 Solution No. 6: Standardized Prototype Placement and Setup Geometry

Prototype repositioning or portability was not established as an independent root cause of positional error in the preceding root-cause analysis. However, moving the prototype can change already validated operating and testing conditions, including camera position, hand-to-camera distance, viewing angle, workspace lighting, and measurement geometry. Instead of treating portability itself as the technical problem, the proposed solution is to control the setup changes associated with repositioning by standardizing the physical placement and alignment of the lamp, camera, and measurement setup.

Consistent reference positions or alignment marks may be established for the prototype, camera, and measurement instruments during experimental testing. This reduces unnecessary setup variation and helps ensure that changes in gesture-recognition or positional-accuracy results are not caused simply by an inconsistent test arrangement. Because the solution directly maintains already validated factors under controlled conditions, Standardized Prototype Placement and Setup Geometry is considered VALID as an experimental-control solution.

To confirm the effectiveness of the solution during implementation, selected gesture-recognition and positional-accuracy trials may be repeated after the prototype has been moved and returned to its designated reference position. Comparable results after repositioning would indicate that the standardized setup successfully limits unnecessary variation. This additional testing evaluates how effective the solution is in practice; it does not leave the solution itself pending for validation.

#### 2.3.3.7 Solution No. 7: Improved Structural Stiffness and Joint Support

The root-cause validation identified insufficient structural stiffness and joint support as a valid direct potential cause of positioning deviation. Weak joints, structural deflection, excessive loading, loose servo mounts, or sagging links may cause the actual mechanical configuration of the smart lamp to differ from the intended joint configuration even when the correct servo command is received.

Jiao et al. (2022) reports that low structural stiffness can significantly affect robot positional accuracy and identifies link structure, material properties, actuator or transmission stiffness, and configuration as important contributors. Liu et al. (2022) likewise explains that robot positioning accuracy may be affected by load and motion when insufficient stiffness results in joint and end-effector deflection. These findings provide the technical basis for improving mechanical support in the proposed articulated lamp.

During solution validation, the joints, servo mounts, lamp links, and supports will be inspected for looseness, excessive loading, sagging, or visible deflection. Repeated target-angle measurements will be performed using the initial mechanical configuration. If mechanical problems are observed, the affected parts may be tightened, realigned, supported, or reinforced, after which the same target-angle tests will be repeated. The resulting positional error and repeatability will be compared to determine whether the mechanical adjustments improve positioning performance.

### 2.4 Factors Identification

Based on the root cause analysis, servo calibration, hand-to-camera distance, and workspace lighting were selected as factors for consideration in the testing of the three-degree-of-freedom (3-DOF) smart lamp. These factors relate to different aspects of system performance. Servo calibration will be evaluated in terms of joint positional accuracy and repeatability, while hand-to-camera distance and workspace lighting will be evaluated in terms of gesture-recognition reliability. Gesture execution, camera-view obstruction, and structural support will be controlled during testing to reduce their influence on the results.

#### 2.4.1 Servo Calibration Condition

Servo calibration was selected based on the identified root cause concerning servo and control parameters. The prototype will be evaluated before and after calibration to determine whether adjustments to the zero-reference settings and command-to-angle mapping reduce joint positional error. The same target angles and measurement procedure will be used for both conditions. The actual angle of each joint will be measured externally and compared with its commanded angle, while repeated trials will be used to evaluate repeatability.

#### 2.4.2 Hand-to-Camera Distance

Hand-to-camera distance was selected because changes in distance may affect the visibility and apparent size of the hand in the captured image. The gesture-control system will be tested at selected distances to determine whether it correctly recognizes the predefined gestures. The same gesture set, camera position, lighting, and background will be maintained across the distance conditions. The specific distances will be established through preliminary testing and stated in the methodology.

#### 2.4.3 Workspace Lighting Condition

Workspace lighting was selected because insufficient or uneven illumination may affect hand detection and gesture recognition. The system will be evaluated under selected indoor lighting conditions while maintaining a consistent hand-to-camera distance and background. Correct recognitions, incorrect recognitions, and failed detections will be recorded for each condition. The lighting conditions and the method used to document them will be specified in the methodology.

#### 2.4.4 Controlled Conditions During Testing

Gesture execution, hand visibility, and the mechanical condition of the lamp will be kept as consistent as possible during testing. Users will follow the same instructions when performing each gesture, and the camera's view of the hand will remain unobstructed. The prototype will be placed on a stable surface, and its joints and mounting points will be checked for looseness before testing. These conditions will be controlled to help distinguish gesture-recognition problems from physical joint-positioning errors.

---

# Chapter 3 — METHODOLOGY [z][aa]

## 3.1 Design of the Smart Lamp Mechanism [ab]

### 3.1.1 Size of the Lamp

The physical size of the proposed three-degree-of-freedom (3-DOF) smart lamp was determined based on the finalized SolidWorks model. The major dimensions considered in the design include the base diameter, shoulder length, elbow length, lamp head axial length, and lamp head front opening diameter. These dimensions were used as the basis for the fabrication and assembly of the prototype.

[figure — in source doc only]
[figure — in source doc only]
[figure — in source doc only]

As shown in the figures, the proposed smart lamp has a base diameter of 20.00 cm, a shoulder length of 32.88 cm, and an elbow length of 27.08 cm. The lamp head has an axial length of 16.98 cm and a front opening diameter of 13.24 cm. These measurements represent the dimensions of the finalized SolidWorks model.

### 3.1.2 Range of Motion

[figure — in source doc only]

*(empty in source)*

### 3.1.3 Weight of the Lamp

*(empty in source)*

### 3.1.4 Actuators [ac]

*(empty in source)*

### 3.1.5 Microcontroller Selection [ad]

[figure — in source doc only]

The proposed three-degree-of-freedom smart lamp will use an Arduino Mega 2560 Rev3 as the main microcontroller of the system. Its primary purpose is to receive control commands from either the gesture-based control system or the Bluetooth-based mobile application and convert these commands into the appropriate control signals for the lamp's components.

The Arduino Mega 2560 will control the three servo motors responsible for the movement of the base, shoulder, and elbow/lamp-head mechanism. Based on the command received, the microcontroller will instruct the corresponding servo motor to move to the desired angle within the defined range of motion. It will also control the lamp's lighting circuit through the connected switching or PWM control circuit.

[figure — in source doc only]

The Raspberry Pi Zero 2 W is the brain for the camera-controlled gesture system in the smart lamp that is suggested. It gets the video from the camera that is connected and looks at each picture using a Python program that uses computer vision and gesture recognition tools. The Raspberry Pi spots the hand gestures that the user makes and turns those gestures into movement instructions for the smart lamp. The Arduino Mega 2560 gets those instructions, understands them and sends the signals to the servo motors. This way the Raspberry Pi Zero 2 W takes care of the gesture processing. Let the Arduino focus on handling the lamp's hardware and three movements.

[figure — in source doc only]

The HC-05 Bluetooth Module acts as a communication tool that lets the smart lamp receive instructions from a mobile app. It talks to the Arduino Mega 2560 through UART communication, getting the commands that the mobile device sends via Bluetooth. The Arduino then reads these commands. Creates the proper control signals, for the servo motors and the LED.

In hybrid control setup the HC-05 provides the mobile-control mode while the Raspberry Pi Zero 2 W takes care of the gesture-control processing.

[figure — in source doc only]

The Pi Zero Camera Module will watch the users hand movements within its field of view. It will capture the visual data, for the gesture-control system. The images or video frames it captures will be sent to the Raspberry Pi Zero 2 W. There the gesture-recognition system, which has been set up will analyze the data. It will look for the specific gestures the user has pre-set. Once a gesture is recognized it will be turned into a command. This command will then be used to control the lamp.

### 3.1.6 Voltage Level

*(empty in source)*

### 3.1.7 Camera Selection

*(empty in source)*

### 3.1.8 Smart Lamp: Functionality Testing

*(empty in source)*

## 3.2 Tracking Controller

### 3.2.1. Hand-Tracking Technology

#### 3.2.1.1 Calibration and Accuracy

*(empty in source)*

#### 3.2.1.2 Selection of Software for Image Processing [ae][af][ag][ah]

Python, OpenCV, and MediaPipe will be used to develop the hand-gesture control subsystem of the smart lamp. Python will serve as the programming language, while OpenCV will handle camera-frame acquisition, color conversion, and display of the processed frames. MediaPipe will load a pretrained model from a .task file to process the hand input and obtain hand landmark coordinates. These tools were selected because they support camera-based hand processing and integration with the lamp-control program.

The program will use the recognition output to identify the predefined gestures assigned to lamp-control commands. Each accepted gesture will be mapped to its corresponding command and transmitted to the microcontroller for execution. The pretrained model will be used without additional training or fine-tuning. Its role in processing hand input is separate from the trial-and-error calibration used to improve the positional accuracy of the lamp's joints.

[figure — in source doc only]

Figure x

Figure 3.X shows a sample output of the gesture-control program. The hand landmarks are displayed over the camera image, together with the recognized gesture label and its associated score. This image illustrates the program's output and does not represent a measurement of overall gesture-recognition accuracy.

#### 3.2.1.3 Computer/Laptop

*(empty in source)*

#### 3.2.1.4 Data Processing and Analysis

*(empty in source)*

#### 3.2.1.5 Hand-Gesture Tracking Controller: Control System Testing

*(empty in source)*

#### 3.2.1.6 Target Precision/Accuracy Error [ai][aj][ak][al][am][an]

*(empty in source)*

#### 3.2.1.7 Operational Functionalities for Hand Gesture Tracking Controller

| Gesture Illustration | Corresponding Joint Action | Stopping Conditions |
| --- | --- | --- |
| [figure — in source doc only] | Activates the vision-based hand-gesture primary control method. | A deactivation gesture is recognized, or the Bluetooth mobile-control mode is activated |
| [figure — in source doc only] | Deactivates the gesture-based control. | The system enters standby until another activation gesture is recognized. |
| [figure — in source doc only] [figure — in source doc only] | Commands the Lamp-Head Tilt (Pitch) adjustment. | - The joint reaches its mechanical limit of 45° or 135°.<br>- A deactivation gesture is recognized. |
| [figure — in source doc only] [figure — in source doc only] | Commands the Elbow (Pitch) mechanism adjustment. | - The joint reaches its mechanical limit of 30° or 150°.<br>- A deactivation gesture is recognized. |
| [figure — in source doc only] [figure — in source doc only] | Commands the Base Rotation (Yaw) adjustment. | - The joint reaches its mechanical limit of 0° or 350°.<br>- A deactivation gesture is recognized. |

### 3.2.2 Smart-Phone Based Controller

#### 3.2.2.1 Calibration and Accuracy

*(empty in source)*

#### 3.2.2.2 Selection of Software for Mobile Application Development

*(empty in source)*

#### 3.2.2.3 Computer/Laptop/Phone

In the development of the hybrid smart lamp, the computer, laptop, and smartphone each serve distinct, task-specific roles. Unlike setups that rely on a computer for real-time image processing, the laptop or PC in this system is not the main device for handling camera inputs or executing gesture recognition. Instead, it functions exclusively as a development workstation utilized for programming the system's code and building the mobile interface via MIT App Inventor. The smartphone, conversely, acts as the hardware platform for the secondary control method. By running the Bluetooth-enabled mobile application, the phone allows the user to manually transmit angular positioning commands to the lamp's three-degree-of-freedom mechanism. This setup ensures that the smartphone provides a reliable, independent alternative for operating the device when the primary vision-based hand-gesture control is not in use.

#### 3.2.2.4 Data Processing and Analysis

*(empty in source)*

#### 3.2.2.5 Smart-Phone Based Tracking Controller: Control System Testing

*(empty in source)*

#### 3.2.2.6 Target Precision/Accuracy Error

*(empty in source)*

#### 3.2.2.7 Operational Functionalities for Smart-Phone Tracking Controller

*(empty in source)*

## 3.4 Human and Hand-Gesture Acquisition

As shown in Figure 3.X in Section 3.2.1.2, the camera interface displays the detected hand landmarks and the recognized gesture. The user will perform predefined gestures within the camera's field of view to issue lamp-control commands. Each recognized gesture will be mapped to its assigned command and transmitted to the microcontroller. During testing, the hand will remain visible to the camera, and the hand-to-camera distance and lighting conditions will be recorded

## 3.5 Human and Smart-Phone based Acquisition

*(empty in source)*

---

# Comment rail — adviser / editor remarks [a]–[an]

*(These are the review comments attached to the draft, reproduced in full and in order.)*

**[a] Language Quality**

The manuscript contains:

- sentence fragments;
- unnecessary commas;
- capitalization errors;
- inconsistent tense;
- informal language;
- missing apostrophes;
- repeated words;
- incorrect singular and plural forms;
- inconsistent terminology.

Examples that need correction include "arms parts," "the users hand," "arduino," and sentences beginning with "Creates the proper control signals."

**[b] Recommended style**

- Use future tense for procedures not yet conducted - since we ar estill for chapter 1 -3 not 1-5
- Use past tense when describing completed cited studies.
- Use present tense for established facts.
- Avoid first-person language unless the institutional format permits it.
- Prefer concise sentences.
- Define every acronym at first use.

**[c] Priority Revision Checklist**

High Priority

- Finalize "hybrid" versus "dual-mode."
- Revise the Statement of the Problem and objectives.
- Resolve the 350° versus 180° base-motion inconsistency.
- Separate positional-error factors from gesture-recognition factors.
- Complete Chapter 3 procedures and statistical treatment.
- Define all formulas and performance measures.
- Verify the feasibility of the Raspberry Pi Zero 2 W, MediaPipe model, and servo selections.
- Perform torque and power calculations.
- Explain mode-conflict prevention.
- Verify every source and numerical result.

Medium Priority

- Rewrite informal RRS passages.
- Complete the Definition of Terms.
- Improve the literature synthesis.
- Add architecture, wiring, and flow diagrams.
- Add mobile-application details.
- Improve figure quality and numbering.
- Add research ethics and camera-data privacy provisions.

**[d] Final Adviser's Remark:** The project concept is commendable and technically relevant, but the researchers must strengthen the paper's research alignment and measurement design. The clearest recommended direction is to treat the prototype as a dual-mode smart lamp, evaluate gesture and mobile interfaces for command reliability and response time, and evaluate servo calibration primarily through pre-calibration and post-calibration positional error and repeatability. This structure will make the study more defensible, measurable, and technically coherent.

**[e]** The background should follow a clearer progression:

- General development of smart and interactive lighting
- Need for convenient, contactless, and mobile control
- Three-degree-of-freedom lamp positioning
- Problem of servo positional error
- Need for experimental calibration
- Research gap
- Proposed solution

**[f]** The current version becomes highly technical very early. Strengthen the real-world motivation first. Explain what practical inconvenience or limitation the proposed lamp addresses.

**[g] Specific issues**

- Question 1 asks for positional accuracy by gesture and mobile modes.
- Question 2 asks whether the difference between the two is significant.
- Question 3 asks which mode provides the highest accuracy. This overlaps with Question 2.
- Question 4 asks about the effectiveness of a "hybrid control system," although no independent hybrid operating mode is defined.
- Repeatability, recognition reliability, Bluetooth reliability, and response time are mentioned earlier but are absent or incomplete in the research questions.

**[h] Revised version:** This study aims to design and develop a dual-mode gesture-based and mobile-controlled 3-DOF smart lamp and evaluate its functional and positional performance before and after calibration. Specifically, it seeks to answer the following questions:

- What is the functional performance of the developed smart lamp in terms of: 1.1 gesture-command recognition reliability;
- 1.2 Bluetooth mobile-command execution reliability; and
- 1.3 command response time?
- What are the positional error and repeatability of the base, elbow, and lamp-head joints before calibration?
- What are the positional error and repeatability of the three joints after calibration?
- Is there a significant difference between the pre-calibration and post-calibration positional errors of the smart lamp?
- Is there a significant difference in positional error between gesture-based and mobile-based command input when equivalent target angles are used?

**[i] Required corrections**

- Use one term consistently: lamp-head tilt, lamp-head pitch, or head pitch.
- Use one term consistently for the second joint: elbow pitch or arm pitch.
- Distinguish scope from delimitation:
  - Scope states what is included.
  - Delimitation states the intentional boundaries established by the researchers.
- Clearly state the exact number of predefined gestures.
- Specify whether lamp brightness or only mechanical positioning is evaluated.
- State whether the LED lighting function is part of functional testing.
- Explain whether the 0° to 350° base rotation is mechanically and electrically achievable.

**[j] Suggestions**

- Avoid repeatedly using "might" and "may" without stating the concrete potential contribution.
- Add the institution or Computer Engineering program as a beneficiary if appropriate.
- Avoid promising benefits not included in the testing.
- If accessibility is claimed, include an accessibility-related evaluation. Otherwise, phrase it only as a potential application.

**[k] Suggested beneficiary organization**

- Users
- Computer Engineering students
- Faculty and academic institutions
- Embedded-system and HCI researchers
- Future researchers
- Smart-lighting developers

**[l]** Include conceptual and operational definitions for at least:

- 3-DOF
- Absolute positional error
- Arduino Mega 2560
- Bluetooth
- Calibration
- Command reliability
- Dual-mode control
- Gesture recognition
- HC-05
- Hybrid control, if retained
- Open-loop control
- Positional accuracy
- Repeatability
- Response time
- Servo motor
- Target angle
- Actual angle
- Yaw
- Pitch

**[m] Strengths**

The RRL covers the necessary technical areas:

- smart lamps;
- articulated mechanisms;
- degree of freedom;
- gesture recognition;
- Bluetooth control;
- open-loop systems;
- positional accuracy; and
- servo calibration.

**[n] Major recommendations**

- Use a uniform academic tone throughout.
- Avoid excessively long paragraphs.
- End each subsection with a short synthesis connecting the literature to the present study.
- Distinguish clearly among:
  - positional accuracy;
  - recognition accuracy;
  - tracking error;
  - trajectory error; and
  - localization error.
- Do not compare percentages, degrees, and millimeters as if they were directly equivalent.
- Verify that all cited sources appear in the bibliography.
- Check the credibility and retrievability of all 2025 and 2026 sources.
- Add complete citation details for studies where author names are missing in the text.

**[o]** There is a noticeable decline in academic writing quality beginning around Sections 2.2.6 to 2.2.10. Several passages sound informal, repetitive, or incomplete

**[p]** Expressions such as:

- "The arm uses an Arduino Mega 2560 to work."
- "The researchers checked how accurate the arms parts were."
- "This study is similar to the lamp idea."
- "As a result, we can suggest that controlling lamps with 3 degrees of freedom is an easy task."

should be rewritten in formal academic language.

**[q] Suggested standard structure for each study**

- Author and year
- Purpose
- System or methodology
- Important measured results
- Relevance to the present study
- Clear difference or research gap

**[r]** *Marked as resolved*

**[s]** *Re-opened*

**[t]** *Marked as resolved*

**[u]** *Re-opened*

**[v]** Root causes are not fully confirmed until evaluated using prototype data.

The fishbone figure is difficult to read and contains visible editing marks. Regenerate it in high resolution without crossed-out text.

**[w]** *Marked as resolved*

**[x]** *Re-opened*

**[y]** The tables provide useful traceability between literature, causes, solutions, and planned testing.

**[z]** Chapter 3 is incomplete. Many headings have no content, including weight, actuators, voltage level, camera selection, functionality testing, calibration procedures, data processing, target error, and smartphone-controller testing.

**[aa]** Before approval, add:

- research design;
- system architecture;
- hardware and software specifications;
- block diagram;
- wiring diagram;
- bill of materials;
- sampling and trial plan;
- testing procedure;
- data-gathering instruments;
- formulas;
- statistical treatment;
- safety considerations;
- acceptance criteria;
- ethical and privacy considerations for camera data.

**[ab]** material of each structural component, individually even to a screw

- joint bearing or support method;
- cable-routing provisions;
- mechanical stop provisions.

**[ac]** For each servo, document:

- model;
- operating voltage;
- stall torque;
- operating speed;
- range;
- gear material;
- current requirement;
- signal type;
- assigned joint;
- calculated required torque;
- torque safety margin.

A 350° base range may require a special positional servo, multi-turn servo, geared mechanism, or another actuator arrangement. The selected component must support the claimed motion.

**[ad] Required technical clarifications**

- communication protocol between Raspberry Pi and Arduino;
- command format;
- mode-selection logic;
- command-conflict prevention;
- electrical voltage compatibility;
- common-ground arrangement;
- emergency stop behavior;
- startup and reset condition;
- handling of invalid or repeated commands;
- servo power supply separate from the controller supply;
- Bluetooth takeover and gesture-mode deactivation procedure.

**[ae]** Earlier sections describe the method as rule-based and not dependent on machine learning. However, Section 3.2.1.2 says that a pretrained model from a .task file will be used. A pretrained classifier is still a machine-learning component, even if the researchers do not train it themselves.

**[af] Recommended wording:** The system will use a pretrained MediaPipe gesture-recognition model for inference only. The researchers will not conduct model training or fine-tuning. The recognized gesture labels will be mapped through predefined program logic to lamp-control commands.

**[ag] Required details**

- exact MediaPipe task/model;
- model version;
- source and license;
- recognition confidence threshold;
- frame rate;
- gesture confirmation duration;
- debounce or cooldown logic;
- handling of "unknown" gestures;
- left-hand and right-hand treatment;
- number of recognition trials;
- definition of correct, incorrect, and failed recognition.

**[ah] Privacy remark**

Because the system captures camera frames containing a person, state whether images or videos will be stored. If they are stored, include participant consent, data handling, retention, and deletion procedures.

**[ai] Measurement and Statistical Recommendations**

Positional Error

The draft gives:

Absolute Positional Error = |Target Angle − Actual Angle|

This is appropriate, but the following should also be defined:

- Mean absolute error

  MAE = ( Σ_{i=1}^{n} |T_i − A_i| ) / n

- Signed error

  E_i = A_i − T_i

  Signed error helps determine whether the joint consistently overshoots or undershoots.

- Percentage error

  Use percentage error only if it is meaningful for the selected target angle. Avoid it at or near 0°, where division becomes problematic.

**[aj] Positional Accuracy**

The paper should not use "accuracy" without a formula.

Possible definition:

Positional Accuracy (%) = ( 1 − |T − A| / R ) × 100

where R is the defined joint operating range.

However, the researchers must justify this formula. Reporting error in degrees is often clearer and less misleading than converting it to an accuracy percentage.

**[ak] Repeatability**

Repeatability should be measured using repeated trials at the same target angle and starting condition.

Recommended measures:

- standard deviation;
- range;
- variance; or
- maximum deviation from the trial mean.

Use at least three repeated trials per condition, with more trials preferable for a stronger comparison. The final number must be justified and consistently applied.

**[al] Recognition Reliability**

Define as:

Recognition Success Rate (%) = ( Correct Recognitions / Total Attempts ) × 100

Record separately:

- correct recognition;
- incorrect recognition;
- failed detection.

Do not combine incorrect recognition and no detection unless clearly justified.

**[am] Response Time**

Clearly define the start and end points:

- Start: gesture presentation or mobile command transmission
- End: initial servo movement or completion of movement

These are different measures. Select one and apply it consistently.

**[an] Statistical Treatment**

Potential analyses include:

- descriptive statistics for error and repeatability;
- paired comparison for pre-calibration versus post-calibration results;
- comparison of gesture and mobile modes under equivalent target commands;
- comparison across joints;
- comparison across distance and lighting conditions.

The exact inferential test should be selected after examining the data structure and assumptions. State the:

- null and alternative hypotheses;
- significance level;
- test assumptions;
- number of trials;
- unit of analysis.

---

*Captured 2026-10-02 from the Google Doc linked above. Text only — figures, tables-as-images, and
drawings remain in the source document. Re-fetch or re-export if the doc changes.*
