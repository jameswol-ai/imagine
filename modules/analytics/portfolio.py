"""
Portfolio Analytics
"""

class PortfolioAnalytics:

    @staticmethod
    def summary(projects):

        return {

            "total_projects":
                len(projects),

            "active_projects":
                len(
                    [
                        p for p in projects
                        if p.get("status") == "active"
                    ]
                ),

            "total_budget":
                sum(
                    p.get("budget", 0)
                    for p in projects
                )
        }
