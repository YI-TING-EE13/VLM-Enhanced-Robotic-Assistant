# src/task_decomposer.py
from PIL import Image
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

from vlm.vlm_interface import VLMInterface

class TaskDecomposer:
    """
    A service that uses a VLM to decompose a user's task into structured steps.

    This class orchestrates the process of taking a natural language command
    and a visual context (image), generating a specialized prompt, and using a
    VLM service to generate a step-by-step plan. It is designed to produce a
    structured, machine-readable output that can be easily parsed and executed
    by a robotic system.
    """

    def __init__(self, vlm_service: VLMInterface):
        """
        Initializes the TaskDecomposer.

        Args:
            vlm_service (VLMInterface): An instance of a class that adheres to
                                        the VLMInterface, which will be used
                                        to get decisions from a VLM.
        """
        self.vlm_service = vlm_service
        self._prompt_template = self._build_prompt_template()
        print("TaskDecomposer: Service initialized.")

    def decompose_task(self, user_task: str, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Receives a user task and scene image, and returns decomposed steps.

        This method formats the prompt, sends it to the VLM service, and parses
        the markup language response into a structured list of dictionaries.

        Args:
            user_task (str): The user's natural language command (e.g., "get me the apple from the table").
            image (Image.Image): A PIL Image of the current scene.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents a single step in the task plan.
                                  Example:
                                  [
                                      {'step': 1, 'action': 'MOVE_TO', 'target': 'the red apple', 'reason': 'First, move to the target object.'},
                                      {'step': 2, 'action': 'PICK', 'target': 'the red apple', 'reason': 'Pick up the target object.'},
                                  ]

        Raises:
            ValueError: If the VLM's response cannot be parsed correctly.
            Exception: Propagates exceptions from the underlying VLM service.
        """
        print(f"TaskDecomposer: Decomposing task: '{user_task}'")
        final_prompt = self._prompt_template.format(user_task=user_task)
        
        try:
            vlm_response = self.vlm_service.get_decision(text=final_prompt, image=image)
            print("TaskDecomposer: Received response from VLM.")
            return self._parse_vlm_output(vlm_response)
        except Exception as e:
            print(f"TaskDecomposer: An error occurred during task decomposition: {e}")
            raise

    def _build_prompt_template(self) -> str:
        """
        Builds and returns the prompt template for the VLM.

        This prompt is engineered to instruct the VLM to act as a robot task
        planner and to return its plan in a specific XML-like format.

        Returns:
            str: The complete prompt template string.
        """
        return """You are a professional robot task planning assistant. Your duty is to break down complex user commands into a series of simple, concrete, atomic steps, based on the current visual scene.

Please strictly follow the output format below. Do not add any extra explanations or text.

**Output Format:**
<plan>
  <step>
    <action>[ACTION_TYPE]</action>
    <target>[TARGET_OBJECT_DESCRIPTION]</target>
    <reason>[BRIEF_REASON_FOR_THIS_STEP]</reason>
  </step>
  <step>
    <action>[ACTION_TYPE]</action>
    <target>[TARGET_OBJECT_DESCRIPTION]</target>
    <reason>[BRIEF_REASON_FOR_THIS_STEP]</reason>
  </step>
</plan>

**Available [ACTION_TYPE]s:**
- **MOVE_TO**: Move to an object or location.
- **PICK**: Pick up an object.
- **PLACE**: Place the held object somewhere.
- **SCAN**: Scan the environment to find an object or confirm a state.
- **WAIT**: Wait or pause.
- **ASK_CLARIFICATION**: Ask the user a question when the command is ambiguous or there are multiple possible targets.

---
**Example:**

# User Command: \"put that apple in the bowl\"
# Visual Scene: (An image showing a red apple and a white bowl on a table)

# Your Output:
<plan>
  <step>
    <action>MOVE_TO</action>
    <target>the red apple</target>
    <reason>First, I need to move to the target apple.</reason>
  </step>
  <step>
    <action>PICK</action>
    <target>the red apple</target>
    <reason>Pick up the specified apple.</reason>
  </step>
  <step>
    <action>MOVE_TO</action>
    <target>the white bowl</target>
    <reason>Move to the destination for placement.</reason>
  </step>
  <step>
    <action>PLACE</action>
    <target>the white bowl</target>
    <reason>Place the apple in the bowl to complete the task.</reason>
  </step>
</plan>

---
**Now, perform the task based on the following information:**

# User Command: "{user_task}"
# Visual Scene: (The image content will be provided by the API)

# Your Output:
"""

    def _parse_vlm_output(self, vlm_response: str) -> List[Dict[str, Any]]:
        """
        Parses the XML-like string response from the VLM.

        Args:
            vlm_response (str): The raw string response from the VLM, expected
                                to be in the specified <plan> format.

        Returns:
            List[Dict[str, Any]]: A list of step dictionaries.

        Raises:
            ValueError: If the response string is not valid XML or does not
                        follow the expected structure.
        """
        print("TaskDecomposer: Parsing VLM response...")
        try:
            # Clean up potential markdown code blocks
            if '```xml' in vlm_response:
                vlm_response = vlm_response.split('```xml')[1].split('```')[0].strip()
            elif '```' in vlm_response:
                 vlm_response = vlm_response.split('```')[1].split('```')[0].strip()


            root = ET.fromstring(vlm_response)
            if root.tag != 'plan':
                raise ValueError("Root tag is not '<plan>'")

            steps = []
            for i, step_node in enumerate(root.findall('step')):
                step_data = {'step': i + 1}
                action = step_node.find('action')
                target = step_node.find('target')
                reason = step_node.find('reason')

                if action is not None and action.text:
                    step_data['action'] = action.text.strip()
                if target is not None and target.text:
                    step_data['target'] = target.text.strip()
                if reason is not None and reason.text:
                    step_data['reason'] = reason.text.strip()
                
                steps.append(step_data)
            
            print(f"TaskDecomposer: Successfully parsed {len(steps)} steps.")
            return steps

        except ET.ParseError as e:
            print(f"TaskDedecomposer: Failed to parse XML response. Error: {e}")
            print(f"TaskDecomposer: Raw response was:\n---\n{vlm_response}\n---")
            raise ValueError("Received malformed XML response from VLM.")
        except Exception as e:
            print(f"TaskDecomposer: An unexpected error occurred during parsing: {e}")
            raise
