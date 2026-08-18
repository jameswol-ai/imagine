class BoQEngine:

    @staticmethod
    def estimate(area):

        substructure = area * 150
        superstructure = area * 420
        mep = area * 210
        finishes = area * 180

        total = (
            substructure
            + superstructure
            + mep
            + finishes
        )

        return {
            "substructure": substructure,
            "superstructure": superstructure,
            "mep": mep,
            "finishes": finishes,
            "total": total
        }
