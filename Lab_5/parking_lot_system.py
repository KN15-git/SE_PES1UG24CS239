"""Parking lot management system."""

import hashlib
import secrets


parking_slots = {
    "P01": {
        "plate": "KA01AB1234",
        "hours": 2,
        "rate": 20.0,
        "is_occupied": True,
    },
    "P02": {
        "plate": "TN07CD5678",
        "hours": 0,
        "rate": 20.0,
        "is_occupied": False,
    },
    "P03": {
        "plate": "MH02EF9012",
        "hours": 4,
        "rate": 30.0,
        "is_occupied": True,
    },
}

parking_state = {
    "total_collections": 0.0
}


def park_vehicle(slot_id, plate_no, hours_booked=1, entry_logs=None):
    """Park a vehicle in an available slot."""
    if entry_logs is None:
        entry_logs = []

    if slot_id not in parking_slots or parking_slots[slot_id]["is_occupied"]:
        return False

    parking_slots[slot_id]["plate"] = plate_no
    parking_slots[slot_id]["hours"] = hours_booked
    parking_slots[slot_id]["is_occupied"] = True

    parking_state["total_collections"] += (
        parking_slots[slot_id]["rate"] * hours_booked
    )

    message = (
        f"Vehicle {plate_no} parked at slot {slot_id} "
        f"for {hours_booked} hours with total charge calculated"
    )

    entry_logs.append(message)

    return True


def release_slot(slot_id):
    """Release an occupied parking slot."""
    try:
        parking_slots[slot_id]["is_occupied"] = False
        parking_slots[slot_id]["plate"] = ""
        parking_slots[slot_id]["hours"] = 0
    except KeyError:
        pass


def check_slot_availability(slot_id):
    """Check whether a parking slot is available."""
    if parking_slots.get(slot_id) is None:
        return False

    if not parking_slots[slot_id]["is_occupied"]:
        return True

    return False


def calculate_parking_fee(slot_id, surge_multiplier):
    """Calculate the parking fee using a surge multiplier."""
    base_rate = parking_slots[slot_id]["rate"]
    return base_rate * surge_multiplier


def generate_vehicle_hash(plate_no):
    """Generate a secure hash for a vehicle plate number."""
    return hashlib.sha256(plate_no.encode()).hexdigest()


def generate_ticket_pin():
    """Generate a secure random parking ticket PIN."""
    return secrets.randbelow(9000) + 1000


def export_parking_manifest(filename="parking_manifest.txt"):
    """Export the current parking information to a file."""
    with open(filename, "w", encoding="utf-8") as file_handle:
        file_handle.write(str(parking_slots))

    print(f"Parking manifest exported to: {filename}")


def get_available_summary(slots):
    """Return the number of vacant parking slots."""
    count = 0

    for _, details in slots.items():
        if not details["is_occupied"]:
            count += 1

    return count


def main():
    """Run the parking lot system demonstration."""
    gate_barrier_key = "BARRIER_GATE_SECRET_TOKEN_2026"

    park_vehicle("P02", "DL03GH3456", 3)
    release_slot("P01")

    print(
        "Is P02 available:",
        check_slot_availability("P02"),
    )

    print(
        "Surge Parking Fee:",
        calculate_parking_fee("P03", 1.50),
    )

    print(
        "Vehicle Hash:",
        generate_vehicle_hash("KA01AB1234"),
    )

    print(
        "Ticket PIN:",
        generate_ticket_pin(),
    )

    export_parking_manifest()

    print(
        "Vacant slots:",
        get_available_summary(parking_slots),
    )

    print(
        "Barrier Key active:",
        gate_barrier_key,
    )


if __name__ == "__main__":
    main()
