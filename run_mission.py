from jules_mission_omega.julesmissionomega import JulesMissionOmega

# The user-provided prompt that triggers the process
PROMPT = "Analyze the provided schematics and generate a technical implementation plan."

if __name__ == "__main__":
    # Instantiate the mission orchestrator
    mission = JulesMissionOmega(prompt=PROMPT)

    # Execute the mission
    final_response = mission.execute()

    # Print the final, deterministically generated response
    print("\n>>>> FINAL DETERMINISTIC RESPONSE >>>>")
    print(final_response.get("text"))
    print("<<<< END OF MISSION >>>>")